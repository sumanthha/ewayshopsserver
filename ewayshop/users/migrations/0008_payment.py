# Generated by Django 3.1.6 on 2021-07-29 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20210729_1047'),
    ]

    operations = [
        # migrations.CreateModel(
        #     name='Payment',
        #     fields=[
        #         ('id', models.AutoField(primary_key=True, serialize=False)),
        #         ('customer_name', models.CharField(max_length=250, unique=True)),
        #         ('customer_email', models.CharField(blank=True, max_length=250, null=True)),
        #         ('payer_id', models.CharField(blank=True, max_length=250, null=True)),
        #         ('tracking_id', models.CharField(blank=True, max_length=250, null=True)),
        #         ('payment_status', models.CharField(blank=True, max_length=250, null=True)),
        #         ('price', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
        #         ('currency_code', models.CharField(blank=True, max_length=250, null=True)),
        #         ('payment_time', models.DateTimeField(null=True)),
        #     ],
        #     options={
        #         'db_table': 'payment',
        #         'managed': True,
        #     },
        # ),
    ]
