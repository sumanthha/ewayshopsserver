# Generated by Django 3.1.6 on 2021-08-10 05:52

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20210810_1059'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='order',
        #     name='seller_status',
        #     field=models.CharField(choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], max_length=20, null=True),
        # ),
        # migrations.CreateModel(
        #     name='OrderReport',
        #     fields=[
        #         ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('feedback', models.CharField(max_length=450, null=True)),
        #         ('created_on', models.DateTimeField(default=datetime.datetime(2021, 8, 10, 11, 22, 20, 283233))),
        #         ('updated_on', models.DateTimeField(null=True)),
        #         ('is_deleted', models.BooleanField(default=False)),
        #         ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.order')),
        #         ('users_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
        #     ],
        #     options={
        #         'db_table': 'orderreport',
        #         'managed': True,
        #     },
        # ),
    ]
