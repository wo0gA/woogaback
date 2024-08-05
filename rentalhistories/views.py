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


class RentalHistoryList(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        rental_histories = RentalHistory.objects.filter(renter=user)

        RentalHistory.update_rental_info(rental_histories)

        serializer = RentalHistorySerializerForRead(rental_histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EnrollmentHistoryList(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, product_id):
        user = request.user
        rental_histories = RentalHistory.objects.filter(owner=user, product_id=product_id)

        RentalHistory.update_rental_info(rental_histories)

        serializer = RentalHistorySerializerForRead(rental_histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HistoryList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        product_id = request.GET.get('product')
        renter_id = request.GET.get('renter')
        
        product = Product.objects.get(id=product_id)

        rental_histories = RentalHistory.objects.filter(
            product=product_id, 
            owner=product.owner.id, 
            renter=renter_id, 
            ) 
        
        RentalHistory.update_rental_info(rental_histories)
        
        serializer = RentalHistorySerializerForRead(rental_histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

    def post(self, request):
        product_id = request.GET.get('product')
        renter_id = request.GET.get('renter')
       
        product = Product.objects.get(id=product_id)
        
        rental_start_date = datetime.strptime(request.data['rental_start_date'], "%Y-%m-%d").date()
        rental_end_date = datetime.strptime(request.data['rental_end_date'], "%Y-%m-%d").date()
       
       # 대여 가능한 기간인지 확인
        try:
            data = RentalHistory.is_rental_available(product_id, rental_start_date, rental_end_date)
            if data['availability']:
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
            
            serializer = RentalHistorySerializerForRead(data['conflicting_days'], many=True)
            return Response({'message': '해당 기간은 대여가 불가능합니다.', 'conflicting_days': serializer.data}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            return Response({'message': '날짜 설정이 잘못되었습니다.'}, status=status.HTTP_400_BAD_REQUEST)


class HistoryListDetail(APIView):
    permission_classes = [IsAuthenticated] 

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
           