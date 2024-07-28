from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import *
from .serializers import *
from products.models import *
from django.shortcuts import get_object_or_404
from rest_framework.permissions import *


class ProductList(APIView):
    #permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        data = request.data
        data['owner'] = request.user.id
        serializer = ProductSerializerForWrite(data=data)
        if serializer.is_valid():
            product = serializer.save()
            serializer = ProductSerializerForRead(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializerForRead(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductDetail(APIView):
    #permission_classes = [IsAuthenticatedOrReadOnly]
    #조회수 계산 로직 추가 필요

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        #product = Product.count_views(product)  # 제품의 조회수 계산
        serializer = ProductSerializerForRead(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        serializer = ProductSerializerForWrite(product, data=request.data, partial=True)
        if serializer.is_valid():
            product = serializer.save()
            serializer = ProductSerializerForRead(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.erros, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
            
class ReviewList(APIView):
    # permission_classes = [HaveRentedOrReadOnly]   # 대여한 사용자만 post 가능, 아니면 read-only

    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializerForRead(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        data = {
            'product': product.id,
            'writer': request.user.id,
            'star': request.data['star'],
            'comment': request.data['comment'],
        }

        serializer = ReviewSerializerForWrite(data=data)
        if serializer.is_valid():
            review = serializer.save()
            serializer = ReviewSerializerForRead(review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryList(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)