# Generated by Django 5.0.7 on 2024-08-01 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_remove_product_long_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='direct_dealing_place',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='희망 직거래 장소'),
        ),
        migrations.AlterField(
            model_name='review',
            name='comment',
            field=models.CharField(max_length=64, verbose_name='product에 대한 코멘트'),
        ),
    ]