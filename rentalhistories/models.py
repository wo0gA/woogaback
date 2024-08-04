from django.db import models
from products.models import *
from datetime import date
from django.core.exceptions import ValidationError

class RentalHistory(BaseModel):

    # 수정필요
    STATES = (
        ('SCHEDULED','일정확정'),   # 히스토리 인스턴스 생성
        ('IN_USE','사용중'),    # 시작날짜 도래하면 사용중으로 변경
        ('RETURNED','반납완료'),   # 반납완료 버튼 누르면 반납완료로 변경
    )
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, verbose_name='제품', related_name='rentalhistories', on_delete=models.CASCADE)
    renter = models.ForeignKey(User, verbose_name='대여자', related_name='renter_histories', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, verbose_name='소유자', related_name='owner_histories', on_delete=models.CASCADE)
    rental_start_date = models.DateField(verbose_name='대여 시작날짜')
    rental_end_date = models.DateField(verbose_name='대여 종료날짜')
    remaining_days = models.IntegerField(verbose_name='남은 대여기간', default=0) 
    state = models.CharField(choices=STATES, verbose_name='대여 상태', max_length=16, default='SCHEDULED') 
    
    class Meta:
        ordering = ['-created_at']
 
        
    def is_rental_available(product_id, rental_start_date, rental_end_date, rentalhistory_id=None):
        today = date.today()
        
        # 대여시작날짜가 오늘보다 이른 경우 예외처리
        if rental_start_date < today:
            raise ValidationError('대여시작날짜 설정이 잘못되었습니다.')

        # 대여종료날짜가 대여시작날짜보다 이른 경우 예외처리
        if rental_end_date <= rental_start_date:
            raise ValidationError('대여종료날짜 설정이 잘못되었습니다.')
        
        # 대여 가능한 날짜인지 확인
        conflicting_rentals = RentalHistory.objects.filter(
            product_id=product_id,
            state__in=['SCHEDULED', 'IN_USE'],
            rental_start_date__lt=rental_end_date,
            rental_end_date__gt=rental_start_date
        )

        # 수정을 하고자하는 예약 히스토리는 필터링에서 무시
        if rentalhistory_id:
            conflicting_rentals = conflicting_rentals.exclude(id=rentalhistory_id)
        
        data = {
            'conflicting_days': conflicting_rentals,
            'availability':  not conflicting_rentals.exists()
        }
        return  data