from rest_framework import response
from users.models import *
from rest_framework.response import Response
from users.serializers import MyTokenObtainPairSerializer,BussinessAdminSerializer,ResetTokenSerializer,BranchSerializer,ManagerProfileSerializer,BranchManagerSerializer,CategorySerializer,SubCategorySerializer
from rest_framework import generics, viewsets, status
from users.permission import has_permission, has_admin_permission,has_customer_permission
from ewayshop.settings import PayPal_SuccessURL,PayPal_FailureURL,merchant_id,paypal_base_url,paypal_client_id,paypal_secret_key,Customer_Signup_URL,Customer_Forget_URL
from users import json
from users.helper import *
from django.views.generic import View
from django.db.models.query_utils import Q
from django.core.exceptions import ObjectDoesNotExist
from users.serializers import *
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.hashers import make_password,check_password
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from users.helper import *
import pandas as pd
import numpy as np
import os
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
import math
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from requests.auth import HTTPBasicAuth
from json import dumps,loads
import requests

class CustomerSignUpView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CustomerSignUpView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        import json as j

        try:
            datas = j.loads(request.body.decode('utf-8'))
            try:
                profile_codes = Profile.objects.latest()
                count=1
                while count<10:
                    profile_code=profile_codes.profile_code[2:]
                    profile_code=int(profile_code)+count
                    profile_code="CU"+str(profile_code)
                    count+=1
                    if Profile.objects.filter(profile_code=profile_code).count() == 0:
                        break
            except Profile.DoesNotExist:
                profile_code="CU"+"1"
            
            group = "customer"

            if 'email' not in datas:
                return json.Response('Email Address is Required',404, False)
            else:
                email = datas['email']

            if 'phone_number' not in datas:
                return json.Response('Phone Number is Required',404, False)
            else:
                phone_number = datas['phone_number']

            ph_count = Profile.objects.filter(phone_number=phone_number,is_customer=True).count()
            email_count = Profile.objects.filter(email=email).count()

            if email_count > 0:
                return json.Response('Email Address already exist',200, False)
            if ph_count > 0:
                return json.Response('Phone Number already exist',200, False)

            ph_count = Profile.objects.filter(phone_number=phone_number).count()
            email_count = Profile.objects.filter(email=email).count()

            if email_count != 0:
                Profile.objects.filter(email=email).update(is_customer = True)
                return json.Response("Created Successfully",200, True)

            if ph_count != 0:
                Profile.objects.filter(phone_number=phone_number).update(is_customer = True)
                return json.Response("Created Successfully",200, True)

            customertbl = Profile(
                profile_code = profile_code,
                email = email,
                phone_number = phone_number,
                is_customer=True,
                is_active=True
                )
            customertbl.save()
            
            #adding user into group
            group = Group.objects.get(name=group)
            group = UserGroup(user=customertbl, group=group)
            group.save()

            token = get_tokens_for_user(customertbl)
            user = Profile.objects.get(email=email)
            time=datetime.now()+timedelta(minutes=2)
            serializer = ResetTokenSerializer(
                data={'user': user.id, 'jwt_token': token['access'],'expire_ts': time})
            if serializer.is_valid():
                serializer.save()

            context = {
                'email': email,
                'signup_url': Customer_Signup_URL+"?email="+email+"&phone_number="+phone_number+"&token="+token['access'],
            }

            subject = "Welcome to eWayshops"
            recepiants = email

            sendCustomMail(context, recepiants, subject,'customer_welcome.html')
            
            return json.Response("Email sent Successfully",201, True)
        except:
            return json.Response('Admin user cannot signup',200, False)

@csrf_exempt
def save_signup_next(request):
    import json as j

    datas = j.loads(request.body.decode('utf-8'))
    
    password1 = datas['password']
    password2 = datas['confirm_password']
    jwt_token = datas['jwt_token']
    first_name = datas['first_name']
    last_name = datas['last_name']
    email = datas['email']
    phone_number = datas['phone_number']
    zipcode = datas['zipcode']
    address = datas['address']
    city = datas['city']
    state = datas['state']

    try:
        valid = AuthTokenMstr.objects.get(jwt_token=jwt_token)
    except AuthTokenMstr.DoesNotExist:
        return json.Response('Invalid User',401, True)

    if 'password' not in datas:
        return json.Response('New Password is Required',404, False)
    if 'jwt_token' not in datas: 
        return json.Response('Token is Required',404, False)
    
    if password1 != password2:
        return json.Response('Password not match',200, False)

    profile_id = valid.user.id
    user = Profile.objects.get(id=profile_id)
    if user:

        user.password = make_password(password1)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number
        user.address = address
        user.city = city
        user.state = state
        user.zipcode = zipcode
        user.save()
        return json.Response('Customer created Successfully',200, True)
    else:
        return json.Response('User_Not_Exists',404, False)
    
@csrf_exempt
def ForgetPassword(request):
    import json as j
    datas = j.loads(request.body.decode('utf-8'))
    email = datas['email']

    if 'email' not in datas:
        return json.Response('Email Address is Required',404, False)

    try:
        user = Profile.objects.get(email=email,is_active=True,is_customer=True)
        token = get_tokens_for_user(user)
        time=datetime.now()+timedelta(hours=2)
        serializer = ResetTokenSerializer(
            data={'user': user.id, 'jwt_token': token['access'],'expire_ts': time})

        if serializer.is_valid():
            serializer.save()
        name = Profile.objects.get(email = email).first_name

        context = {
            'email': email,
            'name':name,
            'forgot_password': Customer_Forget_URL + token['access'],
        }

        subject = "Reset Password"
        recepiants = email

        sendCustomMail(context, recepiants, subject,'customer_reset_password.html')
        return json.Response('Email_Sent',200, True)
    except:
        return json.Response('No_User_Found',200, False)
        
@csrf_exempt
def save_reset_password(request):
    import json as j
    datas = j.loads(request.body.decode('utf-8'))
    
    password = datas['password']
    jwt_token = datas['jwt_token']
    
    try:
        valid = AuthTokenMstr.objects.get(jwt_token=jwt_token)
    except AuthTokenMstr.DoesNotExist:
        return json.Response('Invalid User',401, True)

    if 'password' not in datas:
        return json.Response('New Password is Required',404, False)
    if 'jwt_token' not in datas: 
        return json.Response('Token is Required',404, False)

    profile_id = valid.user.id
    user = Profile.objects.get(id=profile_id)
    
    if user:
        newpassword = make_password(password)
        user.password = newpassword
        user.save()
        return json.Response('Password Changed Successfully',200, True)
    else:
        return json.Response('User_Not_Exists',404, False)
    
class StoreListAPIView(viewsets.ViewSet):  

    def get_store_list(self, request, *args, **kwargs):
        
        data = request.data
        if 'latitude' in data:
            if len(data['latitude']) >= 1:
                nearby_id_arr = []
                distance_arr = BranchMstr.objects.raw('SELECT *,( 3959 * acos ( cos ( radians(' +data['latitude'] +')) * cos( radians( latitude ) ) * cos( radians( longitude ) - radians('+data['longitude']+') ) + sin ( radians('+data['latitude']+') ) * sin( radians( latitude ) ) ) ) AS distance FROM branch_master')
                for x in distance_arr:
                    if x.distance <= 5:
                        nearby_id_arr.append(x.id)
                query_set = BranchMstr.objects.filter(id__in = nearby_id_arr)
            else:
                query_set = BranchMstr.objects.all()    
        else:
            query_set = BranchMstr.objects.all()

        if 'zipcode' in data:
            if len(data['zipcode']) > 3:
                query_set = query_set.filter(Q(zipcode=data['zipcode']) | Q(city =data['zipcode']) | Q(state = data['zipcode'])) 
        if 'branch_name' in data:
            query_set = query_set.filter(branch_name__icontains=data['branch_name'])
        count = query_set.count()
        if 'page_count' not in data:
            page_count = 12
        else :
            page_count = data['page_count']
        paginator = Paginator(query_set,page_count)
        page_num = data['page_number']

        try:
            query_set = paginator.page(page_num)
        except PageNotAnInteger:
           
            query_set = paginator.page(1)
        except EmptyPage:
            
            query_set = paginator.page(paginator.num_pages)
        serializer = BranchSerializer(query_set,many=True,context={'user_id': request.user.id})
        
        return Response({
            'status':"OK",
            'message':'Store list',
            'count':count,
            'data':serializer.data,
            'responseCode':status.HTTP_200_OK
            })

    def get_single_storelist(self,request,id):
        try:
            branch = BranchMstr.objects.get(id = id)
        except ObjectDoesNotExist:
            return json.Response("No store exist",404, False)

        if request.method == 'GET':
            serializer = BranchSerializer(branch)
            if serializer:
                return json.Response(serializer.data,200, True) 


class ProductListView(viewsets.ViewSet):
    
    def get_item_list(self, request, *args, **kwargs):
        
        data = request.data
        if 'branch_id' in data:
            branchlist = BranchMstr.objects.filter(id=data['branch_id'])
            itemlist = BranchItem.objects.filter(branch = data['branch_id'], is_deleted=False)
            itemcount = len(itemlist)
            
        if 'category_id' in data:
            itemids = ItemMstr.objects.filter(category_id=data['category_id']).values_list('id',flat=True)
            bnch_ids = BranchItem.objects.filter(item_id__in=itemids).values_list('branch',flat=True)
            itemlist = BranchItem.objects.filter(item_id__in = itemids, is_deleted=False)
            branchlist = BranchMstr.objects.filter(id__in = bnch_ids)
            itemcount = len(itemlist)
            
        if 'category_name' in data:
            cate_id = CategoryMstr.objects.get(category_name=data['category_name']).id
            itemids = ItemMstr.objects.filter(category_id=cate_id).values_list('id',flat=True)
            bnch_ids = BranchItem.objects.filter(item_id__in=itemids).values_list('branch',flat=True)
            itemlist = BranchItem.objects.filter(item_id__in = itemids, is_deleted=False)
            branchlist = BranchMstr.objects.filter(id__in = bnch_ids)
            itemcount = len(itemlist)
        
        # Pagination 
        if 'page_count' not in data:
            page_count = 12
        else :
            page_count = data['page_count']
           
        paginator = Paginator(itemlist,page_count)
        page_num = data['page_number']
        
        try:
            itemlist = paginator.page(page_num)
        except PageNotAnInteger: 
            itemlist = paginator.page(1)
        except EmptyPage:           
            itemlist = paginator.page(paginator.num_pages)
        
        itemlst = []
        
        if len(itemlist)>0:
            item = InventorySerializer(itemlist,many=True)
            
            for x in item.data:
                
                if Cart.objects.filter(item_id=x['item']['id'],user_id=request.user.id).count() > 0:
                    x['quantity'] = Cart.objects.get(item_id=x['item']['id'],user_id=request.user.id).quantity
                else:
                    x['quantity'] = 0
                
            itemlst = item.data
        if len(branchlist) > 0:
            branch=BranchSerializer(branchlist,many=True)
        
        return Response({
                'status':"OK",
                'message':'Item list',
                'count':itemcount,
                'data':itemlst,
                'branchlist':branch.data,
                'responseCode':status.HTTP_200_OK
            })
    
    def get_branch_item_list(self, request, *args, **kwargs):
        
        data = request.data
        
        cate_id = CategoryMstr.objects.get(category_name=data['category_name']).id
        itemids = ItemMstr.objects.filter(category_id=cate_id).values_list('id',flat=True)
        bnch_ids = BranchItem.objects.filter(item_id__in=itemids, branch_id = data['branch_id']).values_list('branch_id',flat = True)
        itemlist = BranchItem.objects.filter(item_id__in = itemids, branch_id = data['branch_id'], is_deleted=False)
        branchlist = BranchMstr.objects.filter(id__in = bnch_ids)
        itemcount = len(itemlist)
        
        # Pagination 
        if 'page_count' not in data:
            page_count = 12
        else :
            page_count = data['page_count']
           
        paginator = Paginator(itemlist,page_count)
        page_num = data['page_number']
        
        try:
            itemlist = paginator.page(page_num)
        except PageNotAnInteger: 
            itemlist = paginator.page(1)
        except EmptyPage:           
            itemlist = paginator.page(paginator.num_pages)
        
        itemlst = []
        
        if len(itemlist)>0:
            item = InventorySerializer(itemlist,many=True)
            for x in item.data:
                
                if Cart.objects.filter(item_id=x['item']['id'],user_id=request.user.id).count() > 0:
                    x['quantity'] = Cart.objects.get(item_id=x['item']['id'],user_id=request.user.id).quantity
                else:
                    x['quantity'] = 0
            itemlst = item.data
        if len(branchlist) > 0:
            branch=BranchSerializer(branchlist,many=True)
        
        return Response({
                'status':"OK",
                'message':'Item list',
                'count':itemcount,
                'data':itemlst,
                'branchlist':branch.data,
                'responseCode':status.HTTP_200_OK
            })
class CustomerProfileDetails(viewsets.ViewSet):
    @has_customer_permission
    def get_customer_profile(self, request, *args, **kwargs):
        try:
            user = self.request.user
            current_user = Profile.objects.get(email=user,is_customer=True)
        except Profile.DoesNotExist:
            return json.Response("Nothing to show",404, False)

        if request.method == "GET":
            serializer = ProfileSerializer(current_user)
            return json.Response(serializer.data,200,True)

    @has_customer_permission
    def update_customer_profile(self, request):
        try:
            user = Profile.objects.get(id=request.user.id, is_customer=True)
        except Profile.DoesNotExist:
            return json.Response("Nothing to update",404, False)

        if request.method == "PUT":
            serializer = ProfileSerializer(user, data=request.data)
            data = {}
            if serializer.is_valid():
                serializer.save()
            return json.Response('Profile Updated Successfully',200,True)
        return json.Response(serializers.errors,404, False)
        
class CustomerCart(viewsets.ViewSet): 
    @has_customer_permission
    def add_cart(self,request):
        datas = request.data

        item_id = datas['item_id']
        user_id = request.user.id
        quantity = datas['quantity']
        force_add = False

        price = BranchItem.objects.get(item_id=item_id).item_price
        item_selling_price = BranchItem.objects.get(item_id=item_id).item_selling_price
        price = price 
        discount = item_selling_price 

        if discount > 0:
            total_price = discount * quantity
        else:
            total_price = price * quantity
       
        if force_add == False: 
            
            id_exist = Cart.objects.filter(user_id=user_id).count() #check user data in cart
            if id_exist > 0:

                old_item_id = Cart.objects.filter(user_id = user_id).values_list('item_id',flat=True) #getting item_id of old user data
                old_store = BranchItem.objects.get(item_id=old_item_id[0]).branch_id
                new_store = BranchItem.objects.get(item_id=item_id).branch_id #getting new store

                if new_store != old_store:
                    return Response({
                    'status':"OK",
                    'message':'Your cart contains products from another store',
                    'flag':1,
                    'responseCode':status.HTTP_200_OK
                }) 
                     
            carttbl = Cart(
                  item_id = item_id,
                  user_id = user_id,
                  price = price,
                  quantity = quantity,
                  discount = discount,
                  total_price = total_price
            )
            carttbl.save()
            
            return Response({
                'status':"OK",
                'message':'New item added to cart',
                'flag':0,
                'responseCode':status.HTTP_200_OK
            })   
             
        else:
            del_exist = Cart.objects.filter(user_id=user_id).delete()
            carttbl = Cart(
                  item_id = item_id,
                  user_id = user_id,
                  price = total_price,
                  quantity = quantity
            )
            carttbl.save()
            return Response({
                'status':"OK",
                'message':'New item added to cart',
                'flag':0,
                'responseCode':status.HTTP_200_OK
            })

    @has_customer_permission
    def update_cart(self, request):
        import json as j
        datas = j.loads(request.body.decode('utf-8'))

        item_id = datas['item_id']
        user_id = request.user.id
        quantity = datas['quantity']
        
        if request.method == 'PUT':
            if quantity == 0:
                del_quan = Cart.objects.filter(user_id=user_id,item_id=item_id).delete()
                return json.Response("Cart Updated Successfully",200, True) 
            get_quantity=Cart.objects.get(user_id=user_id,item_id=item_id).quantity
            
            price = BranchItem.objects.get(item_id=item_id).item_price
            total_price = price * quantity

            if get_quantity > 0:
                quan=Cart.objects.filter(user_id=user_id,item_id=item_id).update(quantity=quantity,price=total_price)
            else:
                del_quan = Cart.objects.filter(user_id=user_id,item_id=item_id).delete()
            return json.Response("Cart Updated Successfully",200, True) 
            
    @has_customer_permission
    def delete_cart(self, request):
        user_id = request.user.id
        try:
            cart_delete = Cart.objects.filter(user_id=user_id).delete()
        except ObjectDoesNotExist:
            return json.Response('Nothing to show',404,False)

        if request.method == 'DELETE':
            return json.Response("deleted success",200, True)
        
    @has_customer_permission
    def view_cart(self, request):
        user_id = request.user.id
        try:
            cart_list = Cart.objects.filter(user_id=user_id)
        except ObjectDoesNotExist:
            return json.Response("No cart found",404, False)

        if request.method == 'GET':
            serializer = CartSerializer(cart_list, many=True)
            arr1 = []
            arr2 = []
            arr3 = []

            for x in serializer.data:
                item_price = BranchItem.objects.get(item_id = x['item_id']).item_price
                item_tax = BranchItem.objects.get(item_id = x['item_id']).item_tax
                x['tax']=float(item_price * (item_tax/100)) * float(x['quantity'])
                arr1.append(x['tax']) 
                
                item_selling_price = BranchItem.objects.get(item_id=x['item_id']).item_selling_price
                price = item_price 
                discount = item_selling_price 
                if discount > 0:
                    total_price = discount * x['quantity']
                else:
                    total_price = price * x['quantity']
                arr2.append(round(total_price))
                arr3.append(x['item_id'])
                x['total_price'] = float(total_price) 
                
            get_branch = BranchItem.objects.filter(item_id__in= arr3).values_list('branch_id')
            branch = BranchMstr.objects.filter(id__in = get_branch)
            branch=BranchSerializer(branch,many=True)
        
            data = {
                'total_tax':sum(arr1),
                'sub_total':sum(arr2),
                'total_amount':sum(arr1) + sum(arr2),
                'data':serializer.data,
                'branchlist':branch.data
            }

            if serializer:
                return json.Response(data,200, True)
       
class CustomerWishList(viewsets.ViewSet):
    @has_customer_permission
    def add_wishlist(self,request):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))
        store_id = datas['store_id']
        user_id = request.user.id
        wishlisttbl = Wishlist(
            store_id = store_id,
            user_id = user_id,
        )
        wishlisttbl.save()

        return json.Response('Wishlist added Successfully',200,True)

    @has_customer_permission
    def remove_wishlist(self,request):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))
        store_id = datas['store_id']
        user_id = request.user.id
        remove = Wishlist.objects.filter(user_id=user_id, store_id=store_id).delete()
    
        return json.Response('Wishlist removed Successfully',200,True)

    @has_customer_permission
    def get_wishlist(self, request):
        user_id = request.user.id

        try:
            wishlist = Wishlist.objects.filter(user_id=user_id)
        except ObjectDoesNotExist:
            return json.Response("No wishlist exist",404, False)

        if request.method == 'GET':
            serializer = WishListSerializer(wishlist, many=True)
            return json.Response(serializer.data,200, True)

class OrderView(viewsets.ViewSet):
    @has_customer_permission
    def get_order_history(self,request,*args,**kwargs):
        try:
            customer_id = Profile.objects.get(id = request.user.id)

            if "status" in request.GET:
                order_status = request.GET['status']

                if order_status == "new":
                    current_user = Order.objects.filter(order_status='New',customer_id=customer_id,is_paid =True).order_by('-order_date')
                if order_status == "rejected":
                    current_user = Order.objects.filter(order_status='Rejected',customer_id=customer_id).order_by('-order_date')
                if order_status == "accepted":
                    current_user = Order.objects.filter(order_status='Accepted',customer_id=customer_id).order_by('-order_date')
                if order_status == "processing":
                    current_user = Order.objects.filter(order_status='Processing',customer_id=customer_id).order_by('-order_date')
                if order_status == "ready for pickup":
                    current_user = Order.objects.filter(order_status='Ready for Pickup',customer_id=customer_id).order_by('-order_date')
                if order_status == "completed":
                    current_user = Order.objects.filter(order_status='Completed',customer_id=customer_id).order_by('-order_date')
                if order_status == "incomplete":
                    current_user = Order.objects.filter(order_status='Incomplete',customer_id=customer_id).order_by('-order_date')
                if order_status == "refund issued":
                    current_user = Order.objects.filter(order_status='Refund Issued',customer_id=customer_id).order_by('-order_date')
                if order_status == "pending":
                    current_user = Order.objects.filter(order_status='Pending',customer_id=customer_id, is_paid =False).order_by('-order_date')
            
                if order_status == "all":
                    current_user = Order.objects.filter(customer_id=customer_id).order_by('-order_date')
            else:
                current_user = Order.objects.filter(customer_id=customer_id, is_paid =True).order_by('-order_date')

            current_user = OrderSerializer(current_user,many=True)
            return Response({
                'status':"OK",
                'message':'Order status list',
                'data1':len(current_user.data),
                'data':current_user.data,
                'responseCode':status.HTTP_200_OK
            })
        except ObjectDoesNotExist:
            return json.Response('Nothing to show',404, False)
    
    @has_customer_permission
    def order_details(self, request, *args, **kwargs):
        import json as j
        datas = j.loads(request.body.decode('utf-8'))
        order_id = datas['order_id']

        try:
            current_user = Order.objects.get(order_id=order_id)
        except ObjectDoesNotExist:
            return json.Response('Nothing to show',404, False)

        if request.method == "POST":
            serializer = OrderSerializer_details(current_user)
            return json.Response(serializer.data,200, True)

    def post_report(self, request):
        user = Profile.objects.get(id=request.user.id)
        order_id = request.data['order_id']
        order = Order.objects.get(order_id=order_id)
        feedback = request.data['feedback']
        data = OrderReport.objects.filter(users_id=user, order_id=order)

        if data.exists():
            report_obj = data.first()
            report_obj.order_id = order
            report_obj.feedback = feedback
            report_obj.users_id = user
            report_obj.save()
            return Response({
                'status': "OK",
                'message': 'Report updated Successfully',
                'responseCode': status.HTTP_200_OK,
            })

        OrderReport.objects.create(**{
            'users_id': user,
            'order_id': order,
            'feedback': feedback
        })

        return Response({
            'status': "OK",
            'message': ' order reported successfully',
            'responseCode': status.HTTP_200_OK
        })

class NotificationListAPIView(viewsets.ViewSet):
    @has_customer_permission
    def get_notification_list(self, request):
        try:
            customer_id = Profile.objects.get(id = request.user.id).id
            notification = Notification.objects.filter(customer_id=customer_id).order_by('-created_on')
            read = Notification.objects.filter(customer_id=request.user.id,cus_read=False).values_list('id',flat=True)

            for data in read:
                user_id = Notification.objects.filter(id=data).update(cus_read=True)
        except Profile.DoesNotExist:
            return json.Response("No notification found",404, False)

        if request.method == 'GET':
            serializer = NotificationSerializer(notification, many=True).data
            
            if serializer: 
                return Response({
                'status':"OK",
                'data':serializer,
                'responseCode':status.HTTP_200_OK
            })
    
    @has_customer_permission
    def notification_count(self, request):
        try:
            customer_id = Profile.objects.get(id = request.user.id).id
            unread = Notification.objects.filter(customer_id=customer_id, cus_read = False).count()
        except Profile.DoesNotExist:
            return json.Response("No notification found",404, False)

        if request.method == 'GET':
            if unread >= 0:
                count = unread
            
            return json.Response(count,200, True)

    @has_customer_permission
    def delete_notification(self, request):
        import json as j
        datas = j.loads(request.body.decode('utf-8'))
        delete_id = datas['delete_id']

        for map in delete_id:
            try:
                customer_id = Profile.objects.get(id = request.user.id).id
                notification = Notification.objects.filter(id=map,customer_id=customer_id).delete()
            except Notification.DoesNotExist:
                return json.Response('Nothing to show',404,False)
            
        return json.Response('Successfully deleted',200, True)  

class OrderInfo(viewsets.ViewSet):
    @has_customer_permission
    def create_order(self, request, *args, **kwargs):
        import re
        import random
        datas = request.data
        
        customer_id = datas['customer_id']
        store_id = datas['store_id']
        customer_phone_no = datas['customer_phone_no']
        amount = datas['total_amount']
        order_date = datas['date']
        order_status = datas['order_status']
        start_time = datas['start_time']
        end_time = datas['end_time']
        pickup_person_type = datas['pickup_person_type']
        pickup_person_name = datas['pickup_person_name']
        pickup_person_phone = datas['pickup_person_phone']
        pickup_address = datas['pickup_address']
        pickup_email = datas['pickup_email']
        pickup_phone = datas['pickup_phone']
        store_name = BranchMstr.objects.get(id = store_id).branch_name
        
        id_exist = Cart.objects.filter(user_id=customer_id).count() #check user data in cart
        if id_exist > 0:
            pass
        else:
            return Response({
                'status':"OK",
                'message':"You could not proceed to pickup details because your cart is empty",
                'responseCode':status.HTTP_200_OK
            })
         
        try:
            order_id = Order.objects.latest('order_date')
            count = 1
            while count < 10:
                order_id = order_id.order_id[5:]
                order_id = int(order_id) + count
                order_id = '{:06}'.format(order_id)
                order_id = "EWS-#" + str(order_id)
                count += 1
                if Order.objects.filter(order_id=order_id).count() == 0:
                    break
        except Order.DoesNotExist:
            order_id = "EWS-#" + "000001"
            
        order = Order(
            order_id = order_id,
            customer_id = customer_id,
            store_id = store_id,
            amount= amount,
            customer_phone_no = customer_phone_no,
            order_date = order_date,
            order_status = order_status,
            pickup_person_type = pickup_person_type,
            pickup_person_name = pickup_person_name,
            pickup_person_phone = pickup_person_phone,
            pickup_address = pickup_address,
            pickup_email = pickup_email,
            pickup_phone = pickup_phone,
            est_from_date = None,
            est_start_time = None,
            est_end_time = None,
            customer_from_date = order_date,
            customer_start_time = start_time,
            customer_end_time = end_time,
            shop_name = store_name,
            payment_status = 'unpaid'
            
        )
        order.save()
        return Response({
                'status':"OK",
                'message':"Order created successfully",
                'order_id':order_id,
                'responseCode':status.HTTP_200_OK
            })
               
    @has_customer_permission
    def payment_option(self, request):
        
        import json as j
        import requests

        datas = j.loads(request.body.decode('utf-8'))
        order_id = datas['order_id']
        order_status = datas['order_status']
        payment_type = datas['payment_type']

        if payment_type == 'Pay on Delivery':
            id_exist = Cart.objects.filter(user_id=request.user.id).count() #check user data in cart
            if id_exist > 0:
                pass
            else:
                return Response({
                    'status':"OK",
                    'message':"You could not proceed because your cart is empty",
                    'responseCode':status.HTTP_200_OK
                }) 

            cart_item = Cart.objects.filter(user_id = request.user.id)
            cart_item = CartSerializer(cart_item, many = True)
            
            for x in cart_item.data:
                price = BranchItem.objects.get(item_id=x['item_id']).item_price
                item_selling_price = BranchItem.objects.get(item_id=x['item_id']).item_selling_price
                price = price 
                discount = item_selling_price 

                if discount > 0:
                    total_price = discount * x['quantity']
                else:
                    total_price = price * x['quantity']
                order_list = OrderList(
                    item_id = x['item_id'],
                    order_id = order_id,
                    quantity = x['quantity'],
                    price = price,
                    total_price = total_price
                )
                order_list.save()
            Cart.objects.filter(user_id=request.user.id).delete()
            branch_id = Order.objects.get(order_id = order_id).store_id
        
            store_name = BranchMstr.objects.filter(id = branch_id)[0].branch_name
            store_address = BranchMstr.objects.filter(id = branch_id)[0].branch_address
            customer_id = request.user.id
            customer_name = Profile.objects.get(id = customer_id).first_name
            cust_phone_no = Profile.objects.get(id = customer_id).phone_number

            notification = Notification(
                order_id = order_id,
                store_id = branch_id,
                customer_id = customer_id,
                title = 'order created',
                description = (f"Your order {order_id} has been placed successfully"),
                store_name = store_name,
                address = store_address,
                customer_name = customer_name,
                phone_no = cust_phone_no,
                order_status = order_status

            )
            notification.save()

            order_list = OrderList.objects.filter(order_id = order_id)
            orderlist_seri = OrderListSerializer(order_list, many = True).data

            arr1 = []
            arr2 = []
            for x in orderlist_seri:
                
                item_price = BranchItem.objects.get(item_id = x['item']['id']).item_price
                item_tax = BranchItem.objects.get(item_id = x['item']['id']).item_tax
                x['tax']=float(item_price * (item_tax/100)) * float(x['quantity'])
                arr1.append(x['tax']) 
                
                item_selling_price = BranchItem.objects.get(item_id=x['item']['id']).item_selling_price
                price = item_price 
                discount = item_selling_price 
                if discount > 0:
                    total_price = discount * x['quantity']
                else:
                    total_price = price * x['quantity']
                arr2.append(round(total_price))
                x['total_price'] = float(total_price) 
            data = {
                'total_tax':round(sum(arr1)),
                'sub_total':sum(arr2),
                'total_amount':sum(arr1) + sum(arr2)
                
            }
            customer_id = request.user.id
            get_store_id = Order.objects.get(order_id = order_id).store_id
            
            if Order.objects.get(order_id = order_id).pickup_person_type == 1 :
                pickup_person_name = Profile.objects.get(id = customer_id).first_name
                pickup_person_phone = Profile.objects.get(id = customer_id).phone_number
            else:
                pickup_person_name = Order.objects.get(order_id = order_id).pickup_person_name
                pickup_person_phone = Order.objects.get(order_id = order_id).pickup_person_phone
           
            store_email = BranchMstr.objects.get(id = get_store_id).branch_email
            name = Profile.objects.get(email = store_email).first_name
            orderdate = Order.objects.get(order_id = order_id).order_date
            pickup_date = Order.objects.get(order_id = order_id).customer_from_date
            prefer_pickup_date = pickup_date.strftime('%Y-%m-%d')
            prefer_pickup_start_time = Order.objects.get(order_id = order_id).customer_start_time
            prefer_pickup_end_time = Order.objects.get(order_id = order_id).customer_end_time

            context_store={
                "email":store_email,
                "order_id":order_id,
                "name":name,
                "order_date":orderdate,
                "prefer_pickup_date":prefer_pickup_date,
                "prefer_pickup_start_time":prefer_pickup_start_time,
                "prefer_pickup_end_time":prefer_pickup_end_time,
                "pickup_person":pickup_person_name,
                "phone_number":pickup_person_phone,
                "payment_type":payment_type,
                "item_details":orderlist_seri,
                "cum":data
            }

            customer_email = request.user.email
            customer_id = request.user.id
            orderdate = Order.objects.get(order_id = order_id).order_date
            pickup_date = Order.objects.get(order_id = order_id).customer_from_date
            prefer_pickup_date = pickup_date.strftime('%Y-%m-%d')
            prefer_pickup_start_time = Order.objects.get(order_id = order_id).customer_start_time
            prefer_pickup_end_time = Order.objects.get(order_id = order_id).customer_end_time
            payment_status = Order.objects.get(order_id = order_id).payment_status
            pickup_address = Profile.objects.get(id = customer_id).address
            
            context_customer={
                "email":customer_email,
                "order_id":order_id,
                "order_date":orderdate,
                "prefer_pickup_date":prefer_pickup_date,
                "prefer_pickup_start_time":prefer_pickup_start_time,
                "prefer_pickup_end_time":prefer_pickup_end_time,
                "pickup_person":pickup_person_name,
                "phone_number":pickup_person_phone,
                "payment_status":payment_status,
                "pickup_address":pickup_address,
                "item_details":orderlist_seri,
                "cum":data
            }
            
            store_subject = 'Order Received'
            customer_subject = 'Order Placed'
            sendCustomMail(context_store, store_email, store_subject,'store_order_placed.html')
            sendCustomMail(context_customer, customer_email, customer_subject,'customer_order_placed.html')
            payment_update = Order.objects.filter(order_id=order_id).update(order_status=order_status, payment_type = payment_type, is_paid =True)

            data = "Order submitted successfully"
        if payment_type == "paypal":
            id_exist = Cart.objects.filter(user_id=request.user.id).count() #check user data in cart
            if id_exist > 0:
                pass
            else:
                return Response({
                    'status':"OK",
                    'message':"You could not proceed because your cart is empty",
                    'responseCode':status.HTTP_200_OK
                })
            cart_item = Cart.objects.filter(user_id = request.user.id)
            cart_item = CartSerializer(cart_item, many = True)

            arr1 = []
            arr2 = []

            for x in cart_item.data:
                price = BranchItem.objects.get(item_id=x['item_id']).item_price
                tax = BranchItem.objects.get(item_id = x['item_id']).item_tax
                x['tax'] = float(price * (tax/100)) * float(x['quantity'])
                arr1.append(x['tax'])

                item_selling_price = BranchItem.objects.get(item_id=x['item_id']).item_selling_price
                price = price 
                discount = item_selling_price 

                if discount > 0:
                    total_price = discount * x['quantity']
                else:
                    total_price = price * x['quantity']
                order_list = OrderList(
                    item_id = x['item_id'],
                    order_id = order_id,
                    quantity = x['quantity'],
                    price = price,
                    total_price = total_price
                )
                order_list.save()
                arr2.append(total_price)
            total_amount = float(sum(arr1)) + float(sum(arr2))
            order_status = "pending"
            order_status_update = Order.objects.filter(order_id = order_id).update(order_status = order_status)
            # paypal_oauth_token 
            
            response_oauth = requests.post(paypal_base_url+'v1/oauth2/token', auth = HTTPBasicAuth(paypal_client_id, paypal_secret_key), data = {'grant_type': 'client_credentials'})
            access_token = response_oauth.json()["access_token"] 
            expire_in = response_oauth.json()["expires_in"]

            # paypal_create_order_api 
            create_order_requests =  {
                "intent": "CAPTURE",
                "application_context": {
                    "brand_name": "eWayShop",
                    "landing_page": "BILLING",
                    "shipping_preference": "NO_SHIPPING",
                    "user_action": "PAY_NOW",
                    "return_url":PayPal_SuccessURL,
                    "cancel_url":PayPal_FailureURL
                },
                "purchase_units": [
                    {
                    "amount": {
                        "currency_code": "USD",
                        "value": round(float(total_amount),2)
                    }
                    }
                ]
                }
            headers = {'Authorization' : "Bearer " + access_token,"Content-Type": "application/json"}
            response_order = requests.post(paypal_base_url+'v2/checkout/orders',data = dumps(create_order_requests) , headers = headers )
            tracking_id = response_order.json()["id"]
            approve_url = response_order.json()["links"][1]["href"]
            
            tracking_request = {
                "tracking_id":tracking_id
                }
            
            respose_tracking_api = requests.put(paypal_base_url+'v1/risk/transaction-contexts/'+merchant_id+tracking_id,data = tracking_request , headers = headers )
            payment_update = Order.objects.filter(order_id=order_id).update(access_token=access_token,token_expire = expire_in,tracking_id=tracking_id,approve_url=approve_url,order_status=order_status, payment_type = payment_type,is_paid =True)
            data = { 
                "order_key":order_id,
                "tracking_id":tracking_id,
                "approve_url":approve_url,
                "return_url":PayPal_SuccessURL,
                "cancel_url":PayPal_FailureURL
            }
        return json.Response(data ,200, True)
   
    @has_customer_permission
    def payment_capture_check(self, request):
        import json as j
        import requests
       
        datas = j.loads(request.body.decode('utf-8'))

        order_id = datas['order_key']

        if "payer_id" in datas:
            payer_id  = datas['payer_id']
        else:
            payer_id = ""
        order_token = datas['order_token']
        if order_id =="":
            return json.Response("Order_id is missing",200, True)
        if order_token =="":
            return json.Response("order_token is missing",200, True)

        order_access_token = Order.objects.get(order_id = order_id).access_token
        
        headers = {'Authorization' : "Bearer " + str(order_access_token),"Content-Type": "application/json","PayPal-Request-Id" : order_token ,"PayPal-Client-Metadata-Id" :order_token}
        response_payment_status_api = requests.post(paypal_base_url+'v2/checkout/orders/'+order_token+'/capture', headers = headers ) 
        api_response = response_payment_status_api.json()

        if "status" in api_response:
            status = api_response["status"]
        else:
            status = "Failure"
            payment = Payment(
                order_id = order_id,
                customer_name = request.user.first_name,
                customer_email = request.user.email,
                payer_id = payer_id,
                tracking_id = None,
                payment_status = "cancelled",
                payment_id = None,
                price = Order.objects.get(order_id = order_id).amount,
                currency_code = "USD",
                payment_time = None
            )
            payment.save()

            update_payment_type = Order.objects.filter(order_id = order_id).update(payment_type = "paypal")
            return json.Response("payment cancelled",200, True)
        order_id = Order.objects.get(order_id = order_id)
        payment_id = api_response["purchase_units"][0]["payments"]["captures"][0]["id"]
        payment_status = api_response["purchase_units"][0]["payments"]["captures"][0]["status"]
        amount = api_response["purchase_units"][0]["payments"]["captures"][0]["amount"]["value"]
        payment_time = api_response["purchase_units"][0]["payments"]["captures"][0]["create_time"]
        given_name = api_response["payer"]["name"]["given_name"]
        surname = api_response["payer"]["name"]["surname"]
        name = given_name + surname
        email = api_response["payer"]["email_address"]
        payer_id = api_response["payer"]["payer_id"]
        tracking_id = api_response["id"]
        currency_code = api_response["purchase_units"][0]["payments"]["captures"][0]["amount"]["currency_code"]

        if status == "COMPLETED" :
            #store in db
            payment = Payment(
                order_id = order_id,
                customer_name = name,
                customer_email = email,
                payer_id = payer_id,
                tracking_id = tracking_id,
                payment_status = payment_status,
                payment_id = payment_id,
                price = amount,
                currency_code = currency_code,
                payment_time = payment_time
            )
            payment.save()
            #update order status
            order_status = 'new'
            order_status_update = Order.objects.filter(order_id=order_id).update(order_status=order_status ,payment_status = payment_status)
            #cart delete
            Cart.objects.filter(user_id=request.user.id).delete()
            #notification
            store_id = Order.objects.get(order_id = order_id).store_id
            store_name = BranchMstr.objects.filter(id = store_id)[0].branch_name
            store_address = BranchMstr.objects.filter(id = store_id)[0].branch_address
            customer_id = request.user.id
            customer_name = Profile.objects.get(id = customer_id).first_name
            cust_phone_no = Profile.objects.get(id = customer_id).phone_number
            notification = Notification(
                order_id = order_id,
                store_id = store_id,
                customer_id = customer_id,
                title = 'order created',
                description = (f"Your order {order_id} has been placed successfully"),
                store_name = store_name,
                address = store_address,
                customer_name = customer_name,
                phone_no = cust_phone_no,
                order_status = order_status
            )
            notification.save()

            order_list = OrderList.objects.filter(order_id = order_id)
            orderlist_seri = OrderListSerializer(order_list, many = True).data

            arr1 = []
            arr2 = []
            for x in orderlist_seri:
                
                item_price = BranchItem.objects.get(item_id = x['item']['id']).item_price
                item_tax = BranchItem.objects.get(item_id = x['item']['id']).item_tax
                x['tax']=float(item_price * (item_tax/100)) * float(x['quantity'])
                arr1.append(x['tax']) 
                
                item_selling_price = BranchItem.objects.get(item_id=x['item']['id']).item_selling_price
                price = item_price 
                discount = item_selling_price 

                if discount > 0:
                    total_price = discount * x['quantity']
                else:
                    total_price = price * x['quantity']
                arr2.append(round(total_price))
                x['total_price'] = float(total_price) 
            data = {
                'total_tax':sum(arr1),
                'sub_total':sum(arr2),
                'total_amount':sum(arr1) + sum(arr2)
                
            }
            customer_id = request.user.id
            get_store_id = Order.objects.get(order_id = order_id).store_id

            if Order.objects.get(order_id = order_id).pickup_person_type == 1 :
                pickup_person_name = Profile.objects.get(id = customer_id).first_name
                pickup_person_phone = Profile.objects.get(id = customer_id).phone_number
            else:
                pickup_person_name = Order.objects.get(order_id = order_id).pickup_person_name
                pickup_person_phone = Order.objects.get(order_id = order_id).pickup_person_phone

            store_email = BranchMstr.objects.get(id = get_store_id).branch_email
            name = Profile.objects.get(email = store_email).first_name
            orderdate = Order.objects.get(order_id = order_id).order_date
            pickup_date = Order.objects.get(order_id = order_id).customer_from_date
            prefer_pickup_date = pickup_date.strftime('%Y-%m-%d')
            prefer_pickup_start_time = Order.objects.get(order_id = order_id).customer_start_time
            prefer_pickup_end_time = Order.objects.get(order_id = order_id).customer_end_time
            payment_type = Order.objects.get(order_id = order_id).payment_type
            
            context_store={
                "email":store_email,
                "order_id":order_id,
                "name":name,
                "order_date":orderdate,
                "prefer_pickup_date":prefer_pickup_date,
                "prefer_pickup_start_time":prefer_pickup_start_time,
                "prefer_pickup_end_time":prefer_pickup_end_time,
                "pickup_person":pickup_person_name,
                "phone_number":pickup_person_phone,
                "payment_type":payment_type,
                "item_details":orderlist_seri,
                "cum":data
            }

            customer_email = request.user.email
            customer_id = request.user.id
            orderdate = Order.objects.get(order_id = order_id).order_date
            pickup_date = Order.objects.get(order_id = order_id).customer_from_date
            prefer_pickup_date = pickup_date.strftime('%Y-%m-%d')
            prefer_pickup_start_time = Order.objects.get(order_id = order_id).customer_start_time
            prefer_pickup_end_time = Order.objects.get(order_id = order_id).customer_end_time
            payment_status = Order.objects.get(order_id = order_id).payment_status
            pickup_address = Profile.objects.get(id = customer_id).address
            context_customer={
                "email":customer_email,
                "order_id":order_id,
                "order_date":orderdate,
                "prefer_pickup_date":prefer_pickup_date,
                "prefer_pickup_start_time":prefer_pickup_start_time,
                "prefer_pickup_end_time":prefer_pickup_end_time,
                "pickup_person":pickup_person_name,
                "phone_number":pickup_person_phone,
                "payment_status":payment_status,
                "pickup_address":pickup_address,
                "item_details":orderlist_seri,
                "cum":data
            }
            
            store_subject = 'Order Received'
            customer_subject = 'Order Placed'
            sendCustomMail(context_store, store_email, store_subject,'store_order_placed.html')
            sendCustomMail(context_customer, customer_email, customer_subject,'customer_order_placed.html') 

        else:
            payment = Payment(
                order_id = order_id,
                customer_name = name,
                customer_email = email,
                payer_id = payer_id,
                tracking_id = tracking_id,
                payment_status = payment_status,
                payment_id = payment_id,
                price = amount,
                currency_code = currency_code,
                payment_time = payment_time
            )
            payment.save()
            
            Cart.objects.filter(user_id=request.user.id).delete()
        data = { 
                "payer_name":name,
                "email_address":email,
                "payment_id":payment_id,
                "payment_status":payment_status,
                "amount":amount,
                "payment_date":payment_time,
                "tracking_id":tracking_id

            }
            
        return json.Response(data,200, True)