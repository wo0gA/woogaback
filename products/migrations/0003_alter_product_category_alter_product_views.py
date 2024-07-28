# Generated by Django 5.0.7 on 2024-07-27 19:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_review_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.category', verbose_name='카테고리'),
        ),
        migrations.AlterField(
            model_name='product',
            name='views',
            field=models.IntegerField(default=0, verbose_name='조회수'),
        ),
    ]
