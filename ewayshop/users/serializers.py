from django.db.models import fields
import requests
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from users.models import Profile, AuthTokenMstr, PaymentMstr, CategoryMstr, Order
from rest_framework.fields import CurrentUserDefault

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token['email'] = user.email
        # token['is_buyer'] = user.is_buyer
        # token['is_seller'] = user.is_seller
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        
        group = UserGroup.objects.get(user_id=self.user)
        grp=Group.objects.get(id=group.group_id)

        # Add extra responses here
        data['email'] = self.user.email
        data['fname'] = self.user.first_name
        data['role'] = grp.name
        data['photo'] = self.user.photo
        data['status']="ok"
        data['message']="logged in successfully"
        data['responseCode']=200
        return data


class BussinessAdminSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields =('id','photo', 'address', 'phone_number', 'first_name', 'last_name', 'landmark','email','state','city','zipcode')

class BranchSerializer(serializers.ModelSerializer):
    wishlist = serializers.SerializerMethodField()
    class Meta:
        model = BranchMstr
        fields =('id','branch_code','branch_name', 'branch_email', 'branch_description', 'branch_address', 'latitude', 'longitude','zipcode','branch_phone','photo','wishlist')
    
    def get_wishlist(self, bnch):
        user_id = self.context.get('user_id')
        return Wishlist.objects.filter(store_id=bnch.id, user_id = user_id).exists()
        

class ProfitSerializer(serializers.ModelSerializer):

    class Meta:
        model=BranchMstr
        fields='__all__'

class BranchSzr(serializers.ModelSerializer):
    
    class Meta:
        model = BranchMstr
        fields =('id','branch_code','branch_name')

class BranchUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BranchMstr
        fields =('branch_name', 'branch_email', 'branch_description', 'branch_address', 'latitude', 'longitude','zipcode','branch_phone')

class BranchManagerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields =('id','address', 'latitude', 'longitude', 'phone_number', 'first_name','email','photo','state','city','zipcode')

class BranchManagerUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields =('address', 'latitude', 'longitude', 'phone_number', 'first_name', 'last_name','landmark','email','photo','state','city','zipcode')

class ResetTokenSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AuthTokenMstr
        fields =('user','jwt_token', 'expire_ts',)

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields =('id','first_name','last_name','address','email','phone_number','photo','zipcode','city','state')

class ManagerProfileSerializer(serializers.ModelSerializer):

    branch = serializers.SerializerMethodField('get_managers')
    def get_managers(self, data):
        manager_ids = BranchManager.objects.values_list('branch_id').filter(manager_id=data.id)
        managers=BranchMstr.objects.filter(id__in=manager_ids)
        managers=BranchSerializer(managers,many=True)
        return managers.data

    class Meta:
        model = Profile
        fields = ('id','profile_code','address', 'latitude', 'longitude', 'phone_number', 'first_name', 'last_name','landmark','gender','email','photo','branch','state','city','zipcode','is_active')

class CustomerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields =('profile_code', 'email','phone_number' ,'address','city','state','zipcode','is_active')

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CategoryMstr
        fields =('id','category_code', 'category_name',)

class SubCategorySerializer(serializers.ModelSerializer):

    parent = serializers.SerializerMethodField('get_parent')
    def get_parent(self, data):
        managers=CategoryMstr.objects.get(id=data.parent_id)
        managers=CategorySerializer(managers)
        return managers.data 

    class Meta:
        model = CategoryMstr
        fields = ('id','category_code','category_name', 'parent',)

class ItemMstrSerializer(serializers.ModelSerializer):

    category=CategorySerializer()
    sub_category=SubCategorySerializer()

    class Meta:
        model = ItemMstr
        fields=('id','item_name','category','sub_category','item_description','item_image')

class ItemMstrSr(serializers.ModelSerializer):

    category=CategorySerializer()
    sub_category=SubCategorySerializer()

    class Meta:
        model = ItemMstr
        fields=('category','sub_category',)

class BranchItemSr(serializers.ModelSerializer):

    class Meta:
        model = BranchItem
        fields = ('item_code','id',)
        depth=1
        
class OrderListSerializer(serializers.ModelSerializer): 

    total_price = serializers.SerializerMethodField('get_total_price')
    def get_total_price(self, data):
        price1 = OrderList.objects.filter(id=data.id).values_list('price',flat=True)
        quantity = OrderList.objects.filter(id=data.id).values_list('quantity',flat=True)
        price = int(sum(price1))*int(sum(quantity))
        return price

    item_code = serializers.SerializerMethodField('get_item_code')
    def get_item_code(self,data):
        branch_id=Order.objects.get(order_id=data.order_id).store_id
        item = BranchItem.objects.filter(item_id=data.item_id,branch_id=branch_id)
        itemcode=BranchItemSr(item,many=True)
        return itemcode.data

    item_category_name = serializers.SerializerMethodField('get_category_name')
    def get_category_name(self,data):
        item_id=ItemMstr.objects.filter(id=data.item_id)
        item_id=ItemMstrSr(item_id,many=True)
        return item_id.data

    class Meta:
        model = OrderList
        fields =('item','quantity','price','total_price','item_code','item_category_name','order_id')
        depth= 1

class ProfileOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields =('id','address', 'phone_number', 'first_name','email','gender','state','city','zipcode')

class OrderReportserializer(serializers.ModelSerializer):

    class Meta:
        model = OrderReport
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):

    orderlist = serializers.SerializerMethodField('get_orderlist')
    def get_orderlist(self, data):
        orderlist=OrderList.objects.filter(order_id=data.order_id)
        orderlist=OrderListSerializer(orderlist,many=True)
        return orderlist.data 

    customerlist = serializers.SerializerMethodField('get_customerlist')
    def get_customerlist(self,data):
        customerlist = Profile.objects.filter(id=data.customer_id)
        customerlist = ProfileOrderSerializer(customerlist,many=True)
        return customerlist.data

    payment_details = serializers.SerializerMethodField('get_payment_details')
    def get_payment_details(self,data):
        payment = Payment.objects.filter(order_id = data.order_id)
        payment = PaymentSerializers(payment,many = True)
        return payment.data

    class Meta:
        model = Order
        fields ="__all__"

class OrderSerializer_details(serializers.ModelSerializer):

    orderlist = serializers.SerializerMethodField('get_orderlist')
    def get_orderlist(self, data):
        orderlist=OrderList.objects.filter(order_id=data.order_id)
        orderlist=OrderListSerializer(orderlist,many = True)
        return orderlist.data 

    customerlist = serializers.SerializerMethodField('get_customerlist')
    def get_customerlist(self,data):
        customerlist = Profile.objects.filter(id=data.customer_id)
        customerlist = ProfileOrderSerializer(customerlist,many=True)
        return customerlist.data

    payment_details = serializers.SerializerMethodField('get_payment_details')
    def get_payment_details(self,data):
        payment = Payment.objects.filter(order_id = data.order_id)
        payment = PaymentSerializers(payment,many = True)
        return payment.data

    order_report_feedback = serializers.SerializerMethodField('get_order_report_feedback')
    def get_order_report_feedback(self,data):
        orderreport = OrderReport.objects.filter(order_id = data.order_id).first()
        orderreport = OrderReportserializer(orderreport)
        return orderreport.data

    class Meta:
        model = Order
        fields ="__all__"

class CommissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Commission
        fields=('id','group_code','name','description','percentage','created_on','updated_on')

class CommissionMapSerializer(serializers.ModelSerializer):

    branch = serializers.SerializerMethodField('get_branches')
    def get_branches(self, data):
        branch_ids = CommissionMapping.objects.values_list('branch_id').filter(commission_id=data.id)
        branches=BranchMstr.objects.filter(id__in=branch_ids)
        branches=BranchSerializer(branches,many=True)
        return branches.data

    class Meta:
        model = Commission
        fields=('id','group_code','name','description','percentage','created_on','updated_on','branch')

class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentMstr
        fields=('id','payment_code','test_mode',)

class InventorySerializer(serializers.ModelSerializer):

    item=ItemMstrSerializer()
    class Meta:
        model = BranchItem
        fields=('item_code','id','item','item_price','item_tax','item_sku','item_count','item_discount_percent','item_selling_price',)
        depth=1

class PaymentSerializers(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields= '__all__'
class Orderserializers(serializers.ModelSerializer):
    
    branchlist = serializers.SerializerMethodField('get_branchlist')
    def get_branchlist(self,data):
        branch = BranchMstr.objects.filter(id=data.store_id)
        branch=BranchSzr(branch,many=True)
        return branch.data

    customerlist = serializers.SerializerMethodField('get_customerlist')
    def get_customerlist(self,data):
        customerlist = Profile.objects.filter(id=data.customer_id).values_list('first_name','phone_number')
        return customerlist

    class Meta:
        model = Order
        fields =('branchlist','customerlist','order_id','amount','order_date','order_status','reason','payment_status','payment_type','customer_phone_no','seller_status')
        depth = 1

class NotificationSerializer(serializers.ModelSerializer):
    
    created_on = serializers.ReadOnlyField(source='get_date')
    class Meta:
        model = Notification
        fields='__all__'

class ItemMstrSerializers(serializers.ModelSerializer):

    class Meta:
        model = ItemMstr
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields= ('id','price','quantity','item','item_id','user_id','discount','total_price','created_on','updated_on',)
        depth=1
        
class WishListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wishlist
        fields=('id','user_id','store','created_on','updated_on')
        depth=1