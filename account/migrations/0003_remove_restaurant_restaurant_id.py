# Generated by Django 5.1.1 on 2024-09-07 18:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_restaurant_restaurant_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='restaurant_id',
        ),
    ]
