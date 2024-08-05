from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import *
from .serializers import *
from products.models import *
from rentalhistories.models import *
from django.shortcuts import get_object_or_404
from rest_framework.permissions import *
from likelion_hackathon.permissions import *
from rentalhistories.serializers import RentalHistorySerializerForRead
from datetime import datetime


class ProductList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        user = request.user
        data = request.data
        data['owner'] = request.user.id
        
        print(data)

        serializer = ProductSerializerForWrite(data=data)
        if serializer.is_valid():
            product = serializer.save()
            User.update_point(user, 50)
            serializer = ProductSerializerForRead(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def get(self, request):
        from django.db.models import Q
        keyword = request.GET.get('keyword', None)  # 검색어 파라미터
        category_str = request.GET.get('category', None)  # 카테고리 파라미터
        order = request.GET.get('order', None)  # 정렬 옵션 파라미터

        products = Product.objects.all()

        # 검색어 기준 필터링
        if keyword:
            Tag.update_views(keyword)
            
            products = products.filter(
                Q(name__icontains=keyword) |
                Q(model_name__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(tags__hashtag__icontains=keyword) |
                Q(direct_dealing_place__icontains=keyword)
            ).distinct()
        
        # 카테고리 기준 필터링
        if category_str:
            category = get_object_or_404(Category, sort=category_str)
            Category.update_views(category)

            # 해당 카테고리의 자식 카테고리 전부 조회
            categories = Category.objects.filter(id=category.id).get_descendants(include_self=True)
        
            # 부모 카테고리일 경우 자식 카테고리까지 포함해서 제품 조회
            products = products.filter(category__in =categories)
        
        # 정렬 옵션 기준 정렬
        if order:
            if order == 'recent':
               products = products.order_by('-created_at')
    
            elif order == 'views':
                products = products.order_by('-views')
    
            elif order == 'min_price':
                products = products.order_by('rental_fee_for_a_day')
    
        serializer = ProductSerializerForRead(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ProductDetail(APIView):
    permission_classes = [IsWriterOrReadOnly]
    
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        Product.update_views(product)  
        serializer = ProductSerializerForRead(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        print(request.data)
        
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
    permission_classes = [IsAuthenticatedOrReadOnly]
   
    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializerForRead(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 반환값에 rental_days 추가 필요
    def post(self, request, product_id):
    
        product = get_object_or_404(Product, id=product_id)
        data = {
            'product': product.id,
            'writer': request.user.id,
            'star': request.data['star'],
            'comment': request.data['comment']
        }

        serializer = ReviewSerializerForWrite(data=data)
        if serializer.is_valid():
            review = serializer.save()
            serializer = ReviewSerializerForRead(review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryList(APIView):
    def get(self, request):
        categories = Category.objects.filter(level=0).prefetch_related('children')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PopularCategoryList(APIView):
    def get(self, request):
        categories = Category.objects.order_by('-views')[:5]
        serializer = SimpleCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class RentalAvailability(APIView):
    def get(self, request, product_id):
        rental_start_date = request.data['rental_start_date']
        rental_end_date = request.data['rental_end_date']
        
        rental_start_date = datetime.strptime(request.data['rental_start_date'], "%Y-%m-%d").date()
        rental_end_date = datetime.strptime(request.data['rental_end_date'], "%Y-%m-%d").date()
       
        data = RentalHistory.is_rental_available(product_id, rental_start_date, rental_end_date)

        if data['conflicting_days']: 
            serializer = RentalHistorySerializerForRead(data['conflicting_days'], many=True)
            return Response({'message': '해당 기간은 대여가 불가능합니다.', 'conflicting_days': serializer.data}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': '해당 기간은 대여가 가능합니다.'}, status=status.HTTP_200_OK)


class PopularProductList(APIView):
    def get(self, request):
        import random
        products = list(Product.objects.order_by('-views')[:50])

        size = min(8, len(products))
        selected_popular_products = random.sample(products, size)

        serializer = ProductSerializerForRead(selected_popular_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ProductRecommendList(APIView):
    def get(self, request):
        import random
        products = list(Product.objects.all())

        size = min(4, len(products))
        selected = random.sample(products, size)

        serializer = ProductSerializerForRead(selected, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductRentalHistory(APIView):
    def get(self, request, product_id):
        rental_histories = RentalHistory.objects.filter(product__id=product_id)
        serializer = RentalHistorySerializerForRead(rental_histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

