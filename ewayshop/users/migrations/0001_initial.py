# Generated by Django 3.1.6 on 2021-07-06 14:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_code', models.CharField(max_length=250, unique=True)),
                ('address', models.CharField(max_length=250, null=True)),
                ('latitude', models.CharField(blank=True, max_length=250, null=True)),
                ('longitude', models.CharField(blank=True, max_length=250, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('first_name', models.CharField(blank=True, max_length=250, null=True)),
                ('last_name', models.CharField(blank=True, max_length=250, null=True)),
                ('landmark', models.CharField(blank=True, max_length=250, null=True)),
                ('gender', models.CharField(blank=True, max_length=250, null=True)),
                ('email', models.CharField(max_length=250, unique=True)),
                ('password', models.CharField(max_length=250, null=True)),
                ('photo', models.CharField(blank=True, max_length=250, null=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True, null=True, verbose_name='date joined')),
                ('last_login', models.DateTimeField(auto_now=True, null=True, verbose_name='last login')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_customer', models.BooleanField(default=False)),
                ('is_store', models.BooleanField(default=False)),
                ('zipcode', models.CharField(blank=True, max_length=250, null=True)),
                ('city', models.CharField(blank=True, max_length=250, null=True)),
                ('state', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'get_latest_by': 'date_joined',
            },
        ),
        migrations.CreateModel(
            name='BranchManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'branch_manager_mapping',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BranchMstr',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('branch_code', models.CharField(max_length=250, unique=True)),
                ('branch_name', models.CharField(blank=True, max_length=250, null=True)),
                ('branch_email', models.CharField(max_length=250, unique=True)),
                ('branch_description', models.CharField(blank=True, max_length=250, null=True)),
                ('branch_address', models.CharField(blank=True, max_length=250, null=True)),
                ('photo', models.CharField(blank=True, max_length=250, null=True)),
                ('latitude', models.CharField(blank=True, max_length=250, null=True)),
                ('longitude', models.CharField(blank=True, max_length=250, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=250, null=True)),
                ('city', models.CharField(blank=True, max_length=250, null=True)),
                ('state', models.CharField(blank=True, max_length=250, null=True)),
                ('branch_phone', models.CharField(blank=True, max_length=250, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('is_rejected', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'branch_master',
                'get_latest_by': 'created_on',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CategoryMstr',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('category_code', models.CharField(max_length=250, unique=True)),
                ('category_name', models.CharField(blank=True, max_length=250, null=True)),
                ('parent_id', models.IntegerField(default=0)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'category_master',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Commission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('group_code', models.CharField(max_length=250, unique=True)),
                ('name', models.CharField(max_length=250)),
                ('description', models.CharField(blank=True, max_length=250, null=True)),
                ('percentage', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'commission',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ItemMstr',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('item_name', models.CharField(blank=True, max_length=250, null=True)),
                ('item_description', models.CharField(blank=True, max_length=250, null=True)),
                ('item_image', models.CharField(blank=True, max_length=250, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.categorymstr')),
                ('sub_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.categorymstr')),
            ],
            options={
                'db_table': 'item_master',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, null=True)),
                ('description', models.CharField(max_length=255, null=True)),
                ('order_id', models.IntegerField(null=True)),
                ('store_id', models.IntegerField(null=True)),
                ('customer_id', models.IntegerField(null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('address', models.CharField(max_length=250, null=True)),
            ],
            options={
                'db_table': 'notification',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('delivery_no', models.CharField(max_length=10, null=True)),
                ('order_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('order_status', models.CharField(choices=[('new', 'new'), ('rejected', 'rejected'), ('accepted', 'accepted'), ('processing', 'processing'), ('ready for pick up', 'ready for pick up'), ('refund issued', 'refund issued'), ('incomplete', 'incomplete'), ('completed', 'completed')], default='new', max_length=20, null=True)),
                ('reason', models.CharField(blank=True, max_length=255, null=True)),
                ('pickup_person_type', models.IntegerField(default=1)),
                ('pickup_person_name', models.CharField(max_length=255, null=True)),
                ('pickup_person_phone', models.CharField(max_length=255, null=True)),
                ('pickup_address', models.CharField(max_length=500, null=True)),
                ('pickup_email', models.CharField(max_length=255, null=True)),
                ('pickup_phone', models.CharField(max_length=255, null=True)),
                ('est_from_date', models.DateTimeField(null=True)),
                ('est_start_time', models.CharField(blank=True, max_length=255, null=True)),
                ('est_end_time', models.CharField(blank=True, max_length=255, null=True)),
                ('customer_from_date', models.DateTimeField(null=True)),
                ('customer_start_time', models.CharField(blank=True, max_length=255, null=True)),
                ('customer_end_time', models.CharField(blank=True, max_length=255, null=True)),
                ('payment_status', models.CharField(max_length=255, null=True)),
                ('payment_type', models.CharField(max_length=255, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.branchmanager')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMstr',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('payment_code', models.CharField(max_length=250, unique=True)),
                ('account_name', models.CharField(blank=True, max_length=250, null=True)),
                ('gateway_name', models.CharField(blank=True, max_length=250, null=True)),
                ('login_id', models.CharField(blank=True, max_length=250, null=True)),
                ('login_password', models.CharField(blank=True, max_length=250, null=True)),
                ('test_mode', models.CharField(blank=True, max_length=250, null=True)),
                ('is_cvv_required', models.CharField(blank=True, max_length=250, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'payment_master',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.branchmstr')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'wishlist',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='auth.group')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_group',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='StoreMstr',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('store_code', models.CharField(blank=True, max_length=250, null=True)),
                ('store_name', models.CharField(blank=True, max_length=250, null=True)),
                ('store_description', models.CharField(blank=True, max_length=250, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('is_rejected', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'store_master',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='OrderList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=6, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.itemmstr')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.order')),
            ],
            options={
                'db_table': 'order_list',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.CharField(max_length=255, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.itemmstr')),
            ],
            options={
                'db_table': 'image',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CommissionMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.branchmstr')),
                ('commission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.commission')),
            ],
            options={
                'db_table': 'commission_mapping',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('quantity', models.IntegerField(default=1)),
                ('discount', models.IntegerField(default=0)),
                ('total_price', models.IntegerField(default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.itemmstr')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'cart',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='branchmanager',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.branchmstr'),
        ),
        migrations.AddField(
            model_name='branchmanager',
            name='manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='BranchItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('item_code', models.CharField(blank=True, max_length=250, null=True)),
                ('manager_id', models.IntegerField(null=True)),
                ('item_price', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('item_discount_percent', models.IntegerField(default=0)),
                ('item_selling_price', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('item_tax', models.DecimalField(decimal_places=2, default=7.5, max_digits=5)),
                ('item_sku', models.CharField(blank=True, max_length=250, null=True)),
                ('item_count', models.IntegerField(null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.branchmstr')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.itemmstr')),
            ],
            options={
                'db_table': 'branch_items',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AuthTokenMstr',
            fields=[
                ('auth_id', models.AutoField(primary_key=True, serialize=False)),
                ('jwt_token', models.TextField()),
                ('expire_ts', models.DateTimeField()),
                ('login_time', models.DateTimeField(auto_now=True)),
                ('ip', models.CharField(blank=True, max_length=250, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'authtoken_mst',
                'managed': True,
            },
        ),
    ]
