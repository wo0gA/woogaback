from django.db import models
from accounts.models import *
from mptt.models import MPTTModel, TreeForeignKey

class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name='생성일시', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일시', auto_now=True)

    class Meta:
        abstract = True

# 초기 카테고리 데이터 생성 필요
class Category(MPTTModel):
    id = models.AutoField(primary_key=True)
    sort = models.CharField(verbose_name='카테고리 종류', max_length=16)
    parent = TreeForeignKey('self', verbose_name='상위 카테고리', related_name='children',  db_index=True, on_delete=models.CASCADE, null=True, blank=True)
    views = models.IntegerField(verbose_name='조회수', default=0)
    
    class Meta:
        ordering = ['tree_id', 'lft']

    class MPTTMeta:
        order_insertion_by = ['sort']

    def update_views(self):
        self.views +=1
        self.save()

# 판매랑 대여랑 나누는 것 필요
class Product(BaseModel):
    TYPES = (
        ('SALE', '판매용'),
        ('RENTAL', '대여용'),
        ('BOTH', '판매/대여용'),
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='제품명', max_length=32)
    description = models.CharField(verbose_name='설명', max_length=64)
    long_description = models.CharField(verbose_name='상세설명', max_length=1024, null=True, blank=True)
    rental_fee_for_a_day = models.IntegerField(verbose_name='일일 대여료')
    rental_fee_for_a_week = models.IntegerField(verbose_name='일주일 대여료', null=True, blank=True)
    rental_fee_for_a_month = models.IntegerField(verbose_name='한달 대여료', null=True, blank=True)
    rental_period_limit = models.IntegerField(verbose_name='최대 대여가능기간')
    direct_dealing_is_allowed = models.BooleanField(verbose_name='직거래 가능여부')
    direct_dealing_place = models.CharField(verbose_name='희망 직거래 장소', max_length=128)
    delivery_fee_is_included = models.BooleanField(verbose_name='배송비 포함여부')
    type = models.CharField(verbose_name='제품 타입', max_length=8, default='RENTAL')
    views = models.IntegerField(verbose_name='조회수', default=0)
    photos = models.JSONField(verbose_name='제품 이미지')
    category = TreeForeignKey(Category, verbose_name='카테고리', related_name='products', on_delete=models.CASCADE, db_index=True, null=True, blank=True)
    owner = models.ForeignKey(User, verbose_name='소유자', related_name='products', on_delete=models.CASCADE)
    
    def update_views(self):
        self.views +=1
        self.save()

    def get_popular_products():
        from django.db.models import Q
        popular_products = Product.objects.filter(
            Q(views__gte=50) |
            (Q(category__views__gte=20) &
            Q(category__parent__isnull=False))
        ).distinct()
        
        return popular_products

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, verbose_name='제품', related_name='tags', on_delete=models.CASCADE)
    hashtag = models.CharField(verbose_name='해시태그', max_length=16, null=True, blank=True)

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, verbose_name='제품', related_name='reviews', on_delete=models.CASCADE)
    writer = models.ForeignKey(User, verbose_name='작성자', related_name='reviews', on_delete=models.CASCADE)
    star = models.IntegerField(verbose_name='owner에 대한 별점평가')
    comment = models.CharField(verbose_name='product에 대한 코멘트', max_length=32)
    
        


   