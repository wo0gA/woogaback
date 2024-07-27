from django.db import models
from accounts.models import *

class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name='생성일시', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일시', auto_now=True)

    class Meta:
        abstract = True

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    sort = models.CharField(verbose_name='카테고리 종류', max_length=16)
    parent = models.ForeignKey('self', verbose_name='상위 카테고리', related_name='child_categories', on_delete=models.CASCADE, null=True, blank=True)

class Product(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='제품명', max_length=32)
    description = models.CharField(verbose_name='설명', max_length=64)
    long_description = models.CharField(verbose_name='상세설명', max_length=1024, null=True, blank=True)
    rental_fee_for_a_day = models.IntegerField(verbose_name='일일 대여료')
    rental_fee_for_a_week = models.IntegerField(verbose_name='일주일 대여료')
    rental_fee_for_a_month = models.IntegerField(verbose_name='한달 대여료', null=True, blank=True)
    rental_period_limit = models.IntegerField(verbose_name='최대 대여가능기간')
    direct_dealing_is_allowed = models.BooleanField(verbose_name='직거래 가능여부')
    direct_dealing_place  = models.CharField(verbose_name='희망 직거래 장소', max_length=128)
    delivery_fee_is_included = models.BooleanField(verbose_name='배송비 포함여부')
    delivery_fee = models.IntegerField(verbose_name='배송비')
    views = models.IntegerField(verbose_name='조회수')
    photos = models.JSONField(verbose_name='제품 이미지')
    category = models.ForeignKey(Category, verbose_name='카테고리', related_name='products', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, verbose_name='소유자', related_name='products', on_delete=models.CASCADE)
    
class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, verbose_name='제품', related_name='tags', on_delete=models.CASCADE)
    hashtag = models.CharField(verbose_name='해시태그', max_length=16)

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, verbose_name='제품', related_name='reviews', on_delete=models.CASCADE)
    writer = models.ForeignKey(User, verbose_name='작성자', related_name='reviews', on_delete=models.CASCADE)
    star = models.IntegerField(verbose_name='owner에 대한 별점평가')
    comment = models.CharField(verbose_name='product에 대한 코멘트', max_length=128)

