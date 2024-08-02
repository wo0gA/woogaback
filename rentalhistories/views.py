from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import *
from .serializers import *
from products.models import *
from django.shortcuts import get_object_or_404
from rest_framework.permissions import *
from datetime import datetime

def update_rental_info():
    print('Update remaining rental days and rental state.')

    today = date.today()
    rental_histories = RentalHistory.objects.filter(rental_end_date__gte=today)
    
    for history in rental_histories:

        # 대여상태 사용중으로 업데이트
        if history.rental_start_date <= today:
            if history.state != 'IN_USE':
                history.state = 'IN_USE'
                history.save()

        # 남은 대여일수 업데이트
        remaining_days = (history.rental_end_date-today).days
        if remaining_days < 0:
            remaining_days = 0
        
        history.remaining_days = remaining_days
        history.save()


class RentalHistoryList(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        rental_histories = RentalHistory.objects.filter(renter=user)
        serializer = RentalHistorySerializerForRead(rental_histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EnrollmentHistoryList(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, product_id):
        user = request.user
        rental_histories = RentalHistory.objects.filter(owner=user, product_id=product_id)
        serializer = RentalHistorySerializerForRead(rental_histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HistoryList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        product_id = request.GET.get('product')
        renter_id = request.GET.get('renter')
        
        product = Product.objects.get(id=product_id)

        history = RentalHistory.objects.filter(
            product=product_id, 
            owner=product.owner.id, 
            renter=renter_id, 
            state='SCHEDULED')
        
        serializer = RentalHistorySerializerForRead(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

    def post(self, request):
        product_id = request.GET.get('product')
        renter_id = request.GET.get('renter')
       
        product = Product.objects.get(id=product_id)
        
        rental_start_date = datetime.strptime(request.data['rental_start_date'], "%Y-%m-%d").date()
        rental_end_date = datetime.strptime(request.data['rental_end_date'], "%Y-%m-%d").date()
       
       # 대여 가능한 기간인지 확인
        availability = RentalHistory.is_rental_available(product_id, rental_start_date, rental_end_date)
        if availability:
            today = date.today()

            rental_history_data = {
                "product": product_id,
                "owner": product.owner.id,
                "renter": renter_id,
                "rental_start_date": rental_start_date,
                "rental_end_date": rental_end_date,
                "remaining_days": (rental_end_date-today).days,
                "state": "SCHEDULED" 
            }

            serializer = RentalHistorySerializerForWrite(data=rental_history_data)
            if serializer.is_valid():
                serializer.save() 
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        raise ValidationError('해당기간은 대여가 불가능합니다.')


class HistoryListDetail(APIView):
    # permission_classes = [IsAuthenticatedOrReadOnly] 수정 필요

    def put(self, request, rentalhistory_id):
        history = get_object_or_404(RentalHistory, id=rentalhistory_id)
        
        # 상태를 변경하는 경우
        if 'state' in request.data:
            state = request.data['state']
            User.update_point(request.user, 100)

            data = {
                'state': state
            }
            serializer = RentalHistorySerializerForWrite(history, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
            
        # 대여 일정을 변경할 경우
        else: 
            new_rental_start_date = datetime.strptime(request.data['new_rental_start_date'], "%Y-%m-%d").date()
            new_rental_end_date = datetime.strptime(request.data['new_rental_end_date'], "%Y-%m-%d").date()
       
            availability = RentalHistory.is_rental_available(history.product.id, new_rental_start_date, new_rental_end_date, rentalhistory_id)
            if availability:
                data = {
                    'rental_start_date': new_rental_start_date,
                    'rental_end_date': new_rental_end_date
                }
                serializer = RentalHistorySerializerForWrite(history, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
            else:
                raise ValidationError('해당기간으로 대여기간 변경이 불가능합니다.')
        

    # 대여 일정을 삭제하는 경우
    def delete(self, request, rentalhistory_id):
        history = get_object_or_404(RentalHistory, id=rentalhistory_id)
        history.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
           