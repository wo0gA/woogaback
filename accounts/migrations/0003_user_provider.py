# Generated by Django 5.0.7 on 2024-07-25 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='provider',
            field=models.CharField(default='', max_length=32),
        ),
    ]