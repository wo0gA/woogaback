# Generated by Django 5.0.7 on 2024-08-04 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_user_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile',
            field=models.ImageField(blank=True, default='profile-default-image.png', null=True, upload_to='', verbose_name='프로필사진'),
        ),
    ]
