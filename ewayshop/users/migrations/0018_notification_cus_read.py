# Generated by Django 3.1.6 on 2021-08-06 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20210805_2301'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='cus_read',
            field=models.BooleanField(default=False),
        ),
    ]
