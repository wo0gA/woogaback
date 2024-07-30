from rest_framework import serializers
from .models import *
from accounts.serializers import *


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'sort', 'children', 'views', 'parent']
    
    def get_children(self, obj):
        if obj.children is not None:
            children = obj.children.all()
            return CategorySerializer(children, many=True).data
        return None
    
class SimpleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'sort', 'views']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class ProductSerializerForWrite(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    
    class Meta:
        model = Product
        exclude = ['views']
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        product = Product.objects.create(**validated_data)
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(**tag_data)
            product.tags.add(tag)
        return product
    
    # count 성능 보완 필요
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        
        # 일반 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # 현재 태그와 새 태그 처리
        current_tags = set(instance.tags.all())
        new_tags = set()

        # 새 태그 데이터 처리
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(**tag_data)
            new_tags.add(tag)

        # 태그 삭제
        tags_to_remove = current_tags - new_tags
        for tag in tags_to_remove:
            # 현재 제품과 연결이 없는 다른 제품이 존재하는지 확인
            if tag.products.count() == 1:  # 현재 제품과만 연결된 경우
                tag.delete()  # 태그 삭제

        # 새로운 태그 설정
        instance.tags.set(new_tags)

        # 제품 저장
        instance.save()
        return instance
    

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']
    
class ProductSerializerForRead(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    owner = SimpleUserSerializer()
    category = SimpleCategorySerializer()

    class Meta:
        model = Product
        fields = '__all__'

class ReviewSerializerForWrite(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = '__all__'


class ReviewSerializerForRead(serializers.ModelSerializer):
    writer = SimpleUserSerializer()

    class Meta:
        model = Review
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    #category = CategorySerializer(many=True)
    #tags = TagSerializer(many=True)
    
    class Meta:
        model = Product
        fields = "__all__"

