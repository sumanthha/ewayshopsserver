# Generated by Django 3.1.6 on 2021-08-02 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20210730_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_id',
            field=models.CharField(max_length=25, primary_key=True, serialize=False),
        ),
    ]
