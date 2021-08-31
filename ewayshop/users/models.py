from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.urls import reverse
from django.core.mail import send_mail
from datetime import datetime, timedelta
from django.utils import timezone, tree
from random import randint
from django.utils.timesince import timesince


class MyAccountManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError("user must have a email")
        user = self.model(
            email=email,
        )
        user.is_superuser = False
        user.is_admin = False
        user.is_staff = False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Profile(AbstractBaseUser):
    profile_code = models.CharField(max_length=250, unique=True)
    address = models.CharField(max_length=250,null=True)
    latitude = models.CharField(max_length=250, blank=True, null=True)
    longitude = models.CharField(max_length=250, blank=True, null=True)
    phone_number = models.CharField(max_length=15,blank=True, null=True)
    first_name = models.CharField(max_length=250,blank=True, null=True)
    last_name = models.CharField(max_length=250,blank=True, null=True)
    landmark = models.CharField(max_length=250,blank=True, null=True)
    gender = models.CharField(max_length=250,blank=True, null=True)
    email = models.CharField(max_length=250, unique=True)
    password = models.CharField(max_length=250,null=True)
    photo = models.CharField(max_length=250, null=True,blank=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True, null=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    is_store = models.BooleanField(default=False)
    zipcode = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=250, blank=True, null=True)
    state = models.CharField(max_length=250, blank=True, null=True)

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS=['name']
    objects = MyAccountManager()

    class Meta:
      get_latest_by = 'date_joined'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

DELIVERY_OPTION = (
    ("Free home delivery", "Free home delivery"),
    ("Delivered by yourself", "Delivered by yourself")
)

def three_day_hence():
    return timezone.now() + timezone.timedelta(days=3)

def random_id():
    return randint(100000, 999999)

class OrderStatusChoice(models.TextChoices):
    NEW = u'new','new'
    REJECTED = u'rejected','rejected'
    ACCEPTED = u'accepted','accepted'
    PROCESSING = u'processing','processing'
    READY_FOR_PICK_UP = u'ready for pick up','ready for pick up'
    REFUND_ISSUED = u'refund issued','refund issued'
    INCOMPLETE = u'incomplete','incomplete'
    COMPLETED = u'completed','completed'

class AuthTokenMstr(models.Model):
    auth_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=False)
    jwt_token = models.TextField(null=False)
    expire_ts = models.DateTimeField(null=False)
    login_time = models.DateTimeField(auto_now=True)
    ip = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'authtoken_mst'

class UserGroup(models.Model):
    user = models.ForeignKey(Profile, related_name='+', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name='+', on_delete=models.CASCADE)
    
    class Meta:
        managed = True
        db_table = 'user_group'

    def __str__(self):
        return str(self.user)

class PaymentMstr(models.Model):
    id = models.AutoField(primary_key=True)
    payment_code = models.CharField(max_length=250, unique=True)
    account_name = models.CharField(max_length=250, blank=True, null=True)
    gateway_name = models.CharField(max_length=250, blank=True, null=True)
    login_id = models.CharField(max_length=250, blank=True, null=True)
    login_password = models.CharField(max_length=250, blank=True, null=True)
    test_mode = models.CharField(max_length=250, blank=True, null=True)
    is_cvv_required = models.CharField(max_length=250, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        managed = True
        db_table = 'payment_master'

class StoreMstr(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Profile, related_name='+', on_delete=models.CASCADE)
    store_code = models.CharField(max_length=250, blank=True, null=True)
    store_name = models.CharField(max_length=250, blank=True, null=True)
    store_description = models.CharField(max_length=250, blank=True, null=True)
    is_active= models.BooleanField(default=False)
    is_rejected= models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        managed = True
        db_table = 'store_master'

class BranchMstr(models.Model):
    id = models.AutoField(primary_key=True)
    branch_code = models.CharField(max_length=250, unique=True)
    branch_name = models.CharField(max_length=250, blank=True, null=True)
    branch_email = models.CharField(max_length=250, unique=True)
    branch_description = models.CharField(max_length=250, blank=True, null=True)
    branch_address = models.CharField(max_length=250, blank=True, null=True)
    photo = models.CharField(max_length=250, null=True,blank=True)
    latitude = models.CharField(max_length=250, blank=True, null=True)
    longitude = models.CharField(max_length=250, blank=True, null=True)
    zipcode = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=250, blank=True, null=True)
    state = models.CharField(max_length=250, blank=True, null=True)
    branch_phone = models.CharField(max_length=250, blank=True, null=True)
    is_active= models.BooleanField(default=False)
    is_rejected= models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        managed = True
        db_table = 'branch_master'
        get_latest_by = 'created_on'

class BranchManager(models.Model):
    branch = models.ForeignKey(BranchMstr, related_name='+', on_delete=models.CASCADE)
    manager = models.ForeignKey(Profile, related_name='+', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, null= True)

    class Meta:
        managed = True
        db_table = 'branch_manager_mapping'


class CategoryMstr(models.Model):
    id = models.AutoField(primary_key=True)
    category_code = models.CharField(max_length=250,unique=True)
    category_name = models.CharField(max_length=250, blank=True, null=True)
    parent_id = models.IntegerField(default=0)
    is_deleted= models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        managed = True
        db_table = 'category_master'

class Commission(models.Model):
    id = models.AutoField(primary_key = True)
    group_code = models.CharField(max_length = 250,unique = True)
    name = models.CharField(max_length = 250, )
    description = models.CharField(max_length = 250, blank = True,null = True)
    percentage = models.DecimalField(default=0, max_digits = 5, decimal_places = 2)
    is_deleted=models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)
    class Meta:
        managed = True
        db_table = 'commission'

class CommissionMapping(models.Model):
    commission=models.ForeignKey(Commission,null=True,blank=True, related_name='+', on_delete=models.CASCADE)
    branch=models.ForeignKey(BranchMstr,null=True,blank=True, related_name='+', on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'commission_mapping'

class ItemMstr(models.Model):
    id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=250, blank=True, null=True)
    category = models.ForeignKey(CategoryMstr,null=True,blank=True, related_name='+', on_delete=models.CASCADE)
    sub_category = models.ForeignKey(CategoryMstr,null=True,blank=True, related_name='+', on_delete=models.CASCADE)
    item_description = models.CharField(max_length=250, blank=True, null=True)
    item_image = models.CharField(max_length=250, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)
    is_deleted=models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'item_master'

class BranchItem(models.Model):
    id = models.AutoField(primary_key=True)
    item_code = models.CharField(max_length=250, blank=True, null=True)
    manager_id = models.IntegerField(null= True)
    item = models.ForeignKey(ItemMstr, related_name='+', on_delete=models.CASCADE)
    branch = models.ForeignKey(BranchMstr, related_name='+', on_delete=models.CASCADE)
    item_price = models.DecimalField(default=0, max_digits = 5, decimal_places = 2)
    item_discount_percent = models.IntegerField(default=0)
    item_selling_price = models.DecimalField(default=0, max_digits = 5, decimal_places = 2)
    item_tax = models.DecimalField(default=7.5, max_digits = 5, decimal_places = 2)
    item_sku = models.CharField(max_length=250, blank=True, null=True)
    item_count = models.IntegerField(null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)
    is_deleted=models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'branch_items'

class SellerStatusChoice(models.TextChoices):
    
    PAID = u'Paid','Paid'
    UNPAID = u'Unpaid','Unpaid'


class Order(models.Model):
    order_id = models.CharField(primary_key=True,max_length=250)
    customer = models.ForeignKey(Profile, related_name='+', on_delete=models.CASCADE)
    store = models.ForeignKey(BranchMstr, related_name='+', on_delete=models.CASCADE)
    amount= models.DecimalField(default=0, max_digits = 6, decimal_places = 2)
    customer_phone_no = models.CharField(max_length=255,null=True)
    order_date = models.DateTimeField(auto_now_add=True,null=True)
    order_status = models.CharField(max_length=20, null=True, choices=OrderStatusChoice.choices,
                                    default=OrderStatusChoice.NEW)
    seller_status = models.CharField(max_length=20, null=True, choices=SellerStatusChoice.choices)
    reason = models.CharField(max_length=255,null = True,blank=True)
    pickup_person_type = models.IntegerField(default=1)
    pickup_person_name = models.CharField(max_length=255,null=True)
    pickup_person_phone = models.CharField(max_length=255,null=True)
    pickup_address = models.CharField(max_length=500,null=True)
    pickup_email = models.CharField(max_length=255,null=True)
    pickup_phone = models.CharField(max_length=255,null=True)
    est_from_date = models.DateTimeField(null=True)
    est_start_time =models.CharField(max_length=255,null=True,blank=True)
    est_end_time = models.CharField(max_length=255,null=True,blank=True)
    customer_from_date = models.DateTimeField(null=True)
    customer_start_time =models.CharField(max_length=255,null=True,blank=True)
    customer_end_time = models.CharField(max_length=255,null=True,blank=True)
    payment_status = models.CharField(max_length=255,null = True)
    payment_type = models.CharField(max_length=255,null = True)
    access_token = models.CharField(max_length=255,null = True)
    token_expire = models.IntegerField(default = 0)
    tracking_id = models.CharField(max_length=500,null = True)
    approve_url = models.CharField(max_length=500,null = True)
    shop_name = models.CharField(max_length=250, blank=True, null=True)
    delivered_on = models.DateTimeField(null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.order_id)

class OrderList(models.Model):
    order = models.ForeignKey(Order, related_name='+', on_delete=models.CASCADE)
    item = models.ForeignKey(ItemMstr, related_name='+', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(default=0, max_digits = 6, decimal_places = 2)
    total_price = models.DecimalField(default=0, max_digits = 6, decimal_places = 2,null=True)

    class Meta:
        managed = True
        db_table = 'order_list'

    def __str__(self):
        return str(self.order_id)

class OrderReport(models.Model):
    users_id = models.ForeignKey(Profile, related_name='+', on_delete=models.CASCADE)
    order_id = models.ForeignKey(Order, related_name='+', on_delete=models.CASCADE)
    feedback = models.CharField(max_length= 450, null= True)
    created_on = models.DateTimeField(default=datetime.now())
    updated_on = models.DateTimeField(null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = "orderreport"

class Notification(models.Model):
    title =  models.CharField(max_length=255,null=True)
    description =models.CharField(max_length=255,null=True)
    order_id = models.CharField(max_length=250,null = True)
    store_id = models.IntegerField(null=True)
    customer_id = models.IntegerField(null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    address = models.CharField(max_length=250,null=True)
    store_name = models.CharField(max_length=250, blank=True, null=True)
    customer_name = models.CharField(max_length=250, blank=True, null=True)
    phone_no = models.CharField(max_length=255,null=True)
    order_status = models.CharField(max_length=255,null=True)
    is_read = models.BooleanField(default=False)
    cus_read = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'notification'

    def get_date(self):
        return timesince(self.created_on).encode('utf-8').decode('cp1252').replace('Â', ' ').encode("ascii", "ignore")

class Image(models.Model):
    item = models.ForeignKey(ItemMstr, related_name='+', on_delete=models.CASCADE) 
    image = models.CharField(max_length=255,null=True)
    
    class Meta:
        managed = True
        db_table = 'image'

class Cart(models.Model):
    user = models.ForeignKey(Profile, related_name='+', on_delete=models.CASCADE)
    item = models.ForeignKey(ItemMstr, related_name='+', on_delete=models.CASCADE)
    price = models.DecimalField(default=0, max_digits = 6, decimal_places = 2)
    quantity = models.IntegerField(default=1)
    discount = models.IntegerField(default = 0)
    total_price = models.IntegerField(default = 0)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        managed = True
        db_table = 'cart'
     
class Wishlist(models.Model):
    user = models.ForeignKey(Profile, related_name='+', on_delete=models.CASCADE)
    store = models.ForeignKey(BranchMstr, related_name='+', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        managed = True
        db_table = 'wishlist'

class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, related_name='+', on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=250, blank=True, null=True)
    customer_email = models.CharField(max_length=250, blank=True, null=True)
    payer_id = models.CharField(max_length=250, blank=True, null=True)
    tracking_id = models.CharField(max_length=250, blank=True, null=True)
    payment_status = models.CharField(max_length=250, blank=True, null=True)
    price = models.DecimalField(default=0, max_digits = 5, decimal_places = 2)
    currency_code = models.CharField(max_length=250, blank=True, null=True)
    payment_id = models.CharField(max_length=250, blank=True, null=True)
    payment_time = models.DateTimeField(null=True)
    
    class Meta:
        managed = True
        db_table = 'payment'

    def __str__(self):
        return str(self.order_id)
