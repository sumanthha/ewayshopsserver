# Generated by Django 3.1.6 on 2021-07-23 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210712_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='access_token',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='token_expire',
            field=models.IntegerField(default=0),
        ),
    ]
