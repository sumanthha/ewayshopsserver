# Generated by Django 3.1.6 on 2021-07-27 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20210726_2341'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='store_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
