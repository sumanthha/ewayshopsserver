# Generated by Django 3.1.6 on 2021-08-12 11:33

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_auto_20210810_2226'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='branchmanager',
        #     name='is_active',
        #     field=models.BooleanField(default=False, null=True),
        # ),
        # migrations.AddField(
        #     model_name='order',
        #     name='delivered_on',
        #     field=models.DateTimeField(null=True),
        # ),
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
        #         ('created_on', models.DateTimeField(default=datetime.datetime(2021, 8, 12, 17, 3, 52, 905876))),
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