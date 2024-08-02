from rest_framework import serializers
from .models import *
from products.serializers import *

class ProductSerializerForRentalHistory(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'photos']  


class RentalHistorySerializerForRead(serializers.ModelSerializer):
    product = ProductSerializerForRentalHistory()

    class Meta:
        model = RentalHistory
        fields = '__all__'


class RentalHistorySerializerForWrite(serializers.ModelSerializer):
    class Meta:
        model = RentalHistory
        fields = '__all__'
