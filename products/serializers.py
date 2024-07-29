from rest_framework import serializers
from .models import *
from accounts.serializers import *

class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'
    
    def get_parent(self, obj):
        if obj.parent is not None:
            return CategorySerializer(obj.parent).data
        return None

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['hashtag']

class ProductSerializerForWrite(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    class Meta:
        model = Product
        fields = '__all__'
    
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
    category = CategorySerializer()

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