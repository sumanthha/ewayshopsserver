# Generated by Django 3.1.6 on 2021-08-07 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_order_shop_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='order_status',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
