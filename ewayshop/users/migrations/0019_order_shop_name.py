# Generated by Django 3.1.6 on 2021-08-06 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_notification_cus_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shop_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]