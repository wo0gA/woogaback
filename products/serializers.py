from rest_framework import serializers
from .models import *
from accounts.serializers import *

class ProductSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    #category = CategorySerializer(many=True)
    #tags = TagSerializer(many=True)
    
    class Meta:
        model = Product
        fields = "__all__"