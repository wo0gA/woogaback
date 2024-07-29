# Generated by Django 5.0.7 on 2024-07-29 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentalhistories', '0003_alter_rentalhistory_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='rentalhistory',
            name='rental_days',
            field=models.IntegerField(default=0, verbose_name='대여기간'),
        ),
        migrations.AlterField(
            model_name='rentalhistory',
            name='state',
            field=models.CharField(choices=[('SCHEDULED', '일정확정'), ('CANCELLED', '거래취소'), ('DEAL_COMPLETED', '거래승인'), ('IN_USE', '사용중'), ('RETURNED', '반납완료'), ('SOLDOUT', '판매완료')], max_length=16, verbose_name='대여 상태'),
        ),
    ]