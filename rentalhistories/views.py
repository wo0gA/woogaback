from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import *
from .serializers import *
from products.models import *
from django.shortcuts import get_object_or_404
from rest_framework.permissions import *

class RentalHistoryStatus(APIView):
    permission_classes = [IsAuthenticated]
   
    def get(self, request):
        histories = RentalHistory.objects.filter(renter=request.user)
       
        deal_completed = histories.filter(state='DEAL_COMPLETED').count()
        in_use = histories.filter(state='IN_USE').count()
        returned = histories.filter(state='RETURNED').count()

        # 대여신청 데이터 추가 필요
        data = {
            '대여신청': '',
            '거래승인': deal_completed,
            '사용중': in_use,
            '반납완료': returned
        }
        return Response(data)


class EnrollmentHistoryStatus(APIView):
    permission_classes = [IsAuthenticated]
   
    def get(self, request):
        histories = RentalHistory.objects.filter(owner=request.user)
       
        enrolled_products = histories.count()
        deal_completed = histories.filter(state='DEAL_COMPLETED').count()
        in_use = histories.filter(state='IN_USE').count()
        returned = histories.filter(state='RETURNED').count()

        data = {
            '등록물품': enrolled_products,
            '거래승인': deal_completed,
            '사용중': in_use,
            '반납완료': returned
        }
        return Response(data)

class RentalHistoryList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        histories = RentalHistory.objects.filter(renter=request.user)
        serializer = RentalHistorySerializerForRead(histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
# post 함수 구현 필요
# put 함수 구현 필요, 반납완료 되면 사용자 포인트 +100p 로직 추가
# 일정변경의 경우 히스토리가 내 것인지 확인하는 것도 필요. 