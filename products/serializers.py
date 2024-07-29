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
        fields = ['id', 'sort']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['hashtag']

class ProductSerializerForWrite(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    class Meta:
        model = Product
        exclude = ['views']
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        product = Product.objects.create(**validated_data)
        for tag_data in tags_data:
            Tag.objects.create(product=product, **tag_data)
        return product
    
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