# Generated by Django 5.0.7 on 2024-07-27 12:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RentalHistory',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일시')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('rental_start_date', models.DateField(verbose_name='대여 시작날짜')),
                ('rental_end_date', models.DateField(verbose_name='대여 종료날짜')),
                ('rental_fee', models.IntegerField(verbose_name='총 대여료')),
                ('state', models.CharField(choices=[('SCHEDULED', '일정확정'), ('DEAL_COMPLETED', '거래승인'), ('IN_USE', '사용중'), ('RETURNED', '반납완료')], max_length=16, verbose_name='대여 상태')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner_histories', to=settings.AUTH_USER_MODEL, verbose_name='대여자')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rentalhistories', to='products.product', verbose_name='제품')),
                ('renter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='renter_histories', to=settings.AUTH_USER_MODEL, verbose_name='대여자')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
