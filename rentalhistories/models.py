from django.db import models
from products.models import *

class RentalHistory(BaseModel):

    STATES = (
        ('SCHEDULED','일정확정'),
        ('CANCELLED','거래취소'),
        ('DEAL_COMPLETED','거래승인'),
        ('IN_USE','사용중'),
        ('RETURNED','반납완료'),
    )
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, verbose_name='제품', related_name='rentalhistories', on_delete=models.CASCADE)
    renter = models.ForeignKey(User, verbose_name='대여자', related_name='renter_histories', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, verbose_name='소유자', related_name='owner_histories', on_delete=models.CASCADE)
    rental_start_date = models.DateField(verbose_name='대여 시작날짜')
    rental_end_date = models.DateField(verbose_name='대여 종료날짜')
    rental_fee = models.IntegerField(verbose_name='총 대여료')
    state = models.CharField(choices=STATES, verbose_name='대여 상태', max_length=16)

    def is_rental_available(product_id, rental_start_date, rental_end_date):
        conflicting_rentals = RentalHistory.objects.filter(
            product_id=product_id,
            state__in=['SCHEDULED', 'DEAL_COMPLETED', 'IN_USE'],
            rental_start_date__lt=rental_end_date,
            rental_end_date__gt=rental_start_date
        )
        return  not conflicting_rentals.exists()