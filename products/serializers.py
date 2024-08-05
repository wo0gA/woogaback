from rest_framework import serializers
from .models import *
from accounts.serializers import *

# category 관련 시리얼라이저
class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'sort', 'children', 'views']
    
    def get_children(self, obj):
        if obj.children is not None:
            children = obj.children.all()
            return CategorySerializer(children, many=True).data
        return None
    

class CategorySerializerForProduct(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField() 

    class Meta:
        model = Category
        fields = ['id', 'sort', 'parent', 'views']

    def get_parent(self, obj):
        if obj.parent is not None:
            return CategorySerializerForProduct(obj.parent).data
        return None


class SimpleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'sort', 'views']


# tag 관련 시리얼라이저
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['hashtag', 'views']


# product 관련 시리얼라이저
class ProductThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductThumbnail
        fields = ['thumbnail']


class ProductSerializerForWrite(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    thumbnails = serializers.ListField(child=serializers.ImageField())
    
    class Meta:
        model = Product
        exclude = ['views']


    def create(self, validated_data):
        import json
        
        tags_data = validated_data.pop('tags', [])
        if tags_data:
            tags_data = json.loads(tags_data[0]) 
        
        thumbnails_data = validated_data.pop('thumbnails', [])
        
        product = Product.objects.create(**validated_data)

        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(hashtag=tag_data['hashtag'])
            product.tags.add(tag)
        
        for thumbnail_data in thumbnails_data:
            ProductThumbnail.objects.create(product=product, thumbnail=thumbnail_data)

        return product
    
    
    # count 성능 보완 필요
    def update(self, instance, validated_data):
        import json

        tags_data = validated_data.pop('tags', [])
        thumbnails_data = validated_data.pop('thumbnails', [])
        
        # 일반 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # 현재 태그와 새 태그 처리
        if tags_data:
            tags_data = json.loads(tags_data[0]) 

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

        if thumbnails_data:
            # 현재 썸네일 삭제
            instance.thumbnails.all().delete()

            # 새 썸네일 추가
            for thumbnail_data in thumbnails_data:
                ProductThumbnail.objects.create(product=instance, thumbnail=thumbnail_data)

        # 제품 저장
        instance.save()
        return instance
    
    
class ProductSerializerForRead(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    owner = UserSerializer()
    category = CategorySerializerForProduct()
    thumbnails = ProductThumbnailSerializer(many=True)

    class Meta:
        model = Product
        fields = '__all__'

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'thumbnails']


# review 관련 시리얼라이저
class ReviewSerializerForWrite(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = '__all__'


class ReviewSerializerForRead(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    writer = SimpleUserSerializer()
   
    class Meta:
        model = Review
        fields = '__all__'


