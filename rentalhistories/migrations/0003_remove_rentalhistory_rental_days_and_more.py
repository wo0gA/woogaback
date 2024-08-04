# Generated by Django 5.0.7 on 2024-08-01 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentalhistories', '0002_remove_rentalhistory_rental_fee_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rentalhistory',
            name='rental_days',
        ),
        migrations.AddField(
            model_name='rentalhistory',
            name='remaining_days',
            field=models.IntegerField(default=0, verbose_name='남은 대여기간'),
        ),
        migrations.AlterField(
            model_name='rentalhistory',
            name='state',
            field=models.CharField(choices=[('SCHEDULED', '일정확정'), ('IN_USE', '사용중'), ('RETURNED', '반납완료')], max_length=16, verbose_name='대여 상태'),
        ),
    ]