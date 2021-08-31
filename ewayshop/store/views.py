from django.db.models.query_utils import Q
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from users.serializers import *
from users.permission import has_store_permission
from users import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.hashers import make_password,check_password
from django.views.generic import View
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from users.helper import *
import pandas as pd
import numpy as np
import os
from rest_framework.response import Response
from rest_framework import generics, viewsets, status

class StoreSignUpView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(StoreSignUpView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))
        try:
            profile_codes = Profile.objects.latest()
            count=1
            while count<10:
                profile_code=profile_codes.profile_code[2:]
                profile_code=int(profile_code)+count
                profile_code="MC"+str(profile_code)
                count+=1
                if Profile.objects.filter(profile_code=profile_code).count() == 0:
                    break
        except Profile.DoesNotExist:
            profile_code="MC"+"1"
        try:
            branch_codes = BranchMstr.objects.latest()
            count=1
            while count<10:
                branch_code=branch_codes.branch_code[2:]
                branch_code=int(branch_code)+count
                branch_code="BC"+str(branch_code)
                count+=1
                if BranchMstr.objects.filter(branch_code=branch_code).count() == 0:
                    break
                
        except BranchMstr.DoesNotExist:
            branch_code="BC"+"1"
        branch_name = datas['branch_name']
        email=datas['email']
        branch_email = datas['email']
        first_name = datas['first_name']
        phone_number = datas['phone_number']
        branch_phone = datas['phone_number']
        address = datas['address']
        branch_address = datas['address']
        latitude = datas['latitude']
        longitude = datas['longitude']
        zipcode = datas['zipcode']
        city = datas['city']
        state = datas['state']

        group= "store"

        if 'email' not in datas:
            return json.Response('Email Address is Required',404, False)
        else:
            email = datas['email']

        branch_count = BranchMstr.objects.filter(branch_name=branch_name).count()
        if branch_count != 0:
            return json.Response("branch name already exist",200, False)
            
        manager = Profile.objects.filter(email=email).count()
        branch = BranchMstr.objects.filter(branch_email=branch_email).count()
        if manager == 0 and branch==0:
            #manage details
            managertbl = Profile(profile_code=profile_code,
            email=email,
            first_name=first_name,
            phone_number=phone_number,
            address=address,
            latitude=latitude,
            longitude=longitude,
            zipcode=zipcode,
            city=city,
            state=state,
            is_store=True)
            
            # branch details
            branchtbl = BranchMstr(branch_code=branch_code,
            branch_name=branch_name,
            branch_email=branch_email,
            branch_phone=branch_phone,
            branch_address=branch_address,
            latitude=latitude,
            longitude=longitude,
            zipcode=zipcode,
            city=city,
            state=state,
            is_active=True
            )
            managertbl.save()
            branchtbl.save()
            #mapping Manager and branch
            branch_map = BranchManager(manager=managertbl,branch=branchtbl)
            branch_map.save()
            #adding user into group
            group = Group.objects.get(name=group)
            group = UserGroup(user=managertbl, group=group)
            group.save()
            token = get_tokens_for_user(managertbl)
            user = Profile.objects.get(email=email)
            time=datetime.now()+timedelta(hours=2)
            serializer = ResetTokenSerializer(
                data={'user': user.id, 'jwt_token': token['access'],'expire_ts': time})
            if serializer.is_valid():
                serializer.save()
                commission_group_ins = CommissionMapping()
                commission_group_ins.commission_id = Commission.objects.get(id=1).id
                commission_group_ins.branch_id = branchtbl.id
                commission_group_ins.save()
            name = Profile.objects.get(email = email).first_name

            context = {
                'email': email,
                'name': name,
                'reset_password_url': "http://13.233.62.76:3000/auth/reset-password/" + token['access'],
            }

            subject = "Welcome to eWayshops"
            recepiants = email

            sendCustomMail(context, recepiants, subject,'store_welcome.html')

            admin = Profile.objects.get(is_admin = True).email
            
            admin_context = {
                'email': email,
                'store_owner_name' : first_name,
                'phone_number' : phone_number,
                'email_address' : email,
                'adress': address
            }

            admin_subject = "New store arrived"

            sendCustomMail(admin_context, admin, admin_subject,'store-admin-signup.html')
        else:
            return json.Response("Email already exist",200, False)

        return json.Response("Store created Successfully",201, True)


class StoreProfileDetails(viewsets.ViewSet):
    @has_store_permission
    def get_store_admin(self, request, *args, **kwargs):
        try:
            user = self.request.user
            current_user = Profile.objects.get(email=user,is_store=True)
        except Profile.DoesNotExist:
            return json.Response("Nothing to show",404, False)

        if request.method == "GET":
            serializer = ManagerProfileSerializer(current_user)
            return json.Response(serializer.data,200,True)

    @has_store_permission
    def update_store_admin(self, request):
        
        import json as j

        datas = j.loads(request.body.decode('utf-8'))

        address = datas['address']
        latitude = datas['latitude']
        longitude = datas['longitude']
        zipcode = datas['zipcode']
        phone_number = datas['phone_number']
        first_name = datas['first_name']
        email = datas['email']
        photo = datas['photo']
        store_img = datas['store_img']
        shop_name = datas['shop_name']
        
        emailcnt = Profile.objects.filter(~Q(id=request.user.id),email=email).count()
        if emailcnt > 0:
            return json.Response("Email already exist",200, False)

        if request.method == 'PUT':
            user=Profile.objects.filter(id=request.user.id).update(address=address,latitude=latitude,longitude=longitude,zipcode=zipcode,phone_number=phone_number,first_name=first_name,email=email,photo=photo)
            branch_user = BranchManager.objects.get(manager_id=request.user.id).branch_id
            branchitemtbl=BranchMstr.objects.filter(id=branch_user).update(photo = store_img,zipcode = zipcode, branch_name = shop_name)

            return json.Response("Profile Updated Successfully",200, True)
        return json.Response("Wrong method call",200, True)
        
class StoreCategory(viewsets.ViewSet):
    @has_store_permission
    def get_subcategory(self, request,category_name, *args, **kwargs):
        try:
            category = CategoryMstr.objects.get(category_name=category_name,is_deleted=False,parent_id=0)
            subcategory = CategoryMstr.objects.filter(parent_id=category.id,is_deleted=False)
        except ObjectDoesNotExist:
            return json.Response("No Subcategory exist",404, False)

        if request.method == 'GET':
            serializer = CategorySerializer(subcategory, many=True)
            if serializer:
                return json.Response(serializer.data,200,True)

    @has_store_permission
    def get_category_store(self, request, *args, **kwargs):
        try:
            sub_category = CategoryMstr.objects.filter(parent_id__gte=1).values_list('parent_id',flat=True)
            category_ids = list(dict.fromkeys(sub_category))  #To remove duplicate id's
            category=CategoryMstr.objects.filter(id__in=category_ids)
        except ObjectDoesNotExist:
            return json.Response("No Category exist",404, False)

        if request.method == 'GET':
            serializer = CategorySerializer(category, many=True)
            if serializer:
                return json.Response(serializer.data,200,True)


class BulkUploadView(viewsets.ViewSet):
    @has_store_permission
    def item_bulk_upload(self, request):
        document = request.data.get('csv')
        
        file_extension = os.path.splitext(document.name)[1]
        if file_extension != ".csv":
            return json.Response('Invalid file format',400, False)
        df = pd.read_csv(document)
        df.dropna(how="all", inplace=True)
        df = pd.DataFrame(df).replace(np.nan, '',regex=True)

        column = list(df.columns)
        column_name=["PRODUCT CODE","NAME","CATEGORY NAME","SUBCATEGORY NAME","SKU","DESCRIPTION","PRICE","SALES TAX","PRODUCT COUNT","DISCOUNT"]

        for x in range(9):            
            if column[x] == f"Unnamed: {x}":
                return json.Response(f"Column name {column_name[x]} is missing",200, True)

            if (list(df.columns)[x]) != column_name[x]:
                return json.Response(f"Invalid column name {column[x]}",200, True)

        row_iter = df.iterrows()
        manager_id = request.user.id
        store_id = BranchManager.objects.get(manager_id = manager_id).branch_id
        for index, row in row_iter:
            
            if row['PRODUCT CODE']=="":
                return json.Response("Product Code is missing",200, True)
            if BranchItem.objects.filter(item_code=row['PRODUCT CODE'], branch_id = store_id).count() > 0:
                return json.Response(f"Product code {row['PRODUCT CODE']} already exist",200, False)
            if row['NAME']=="":
                return json.Response(f"Product Code {row['PRODUCT CODE']} has no NAME",200, True)
            if row['CATEGORY NAME']=="":
                return json.Response(f"Product Code {row['PRODUCT CODE']} has no CATEGORY NAME",200, True)
            try:
                category=CategoryMstr.objects.get(category_name=row['CATEGORY NAME']).id
            except CategoryMstr.DoesNotExist:
                return json.Response(f"No category name '{row['CATEGORY NAME']}' exist",200, True)
            if row['SUBCATEGORY NAME']=="":
                return json.Response(f"Product Code {row['PRODUCT CODE']} has no SUBCATEGORY NAME",200, True)
            try:
                subcategory=CategoryMstr.objects.get(category_name=row['SUBCATEGORY NAME']).parent_id
            except CategoryMstr.DoesNotExist:
                return json.Response(f"No subcategory name '{row['SUBCATEGORY NAME']}' exist",200, True)

            if category != subcategory:
                return json.Response(f"Category name '{row['CATEGORY NAME']}' have no subcategory '{row['SUBCATEGORY NAME']}'",200, True)
            
            if row['SKU']=="":
                return json.Response(f"Product Code {row['PRODUCT CODE']} has no SKU",200, True)
            if BranchItem.objects.filter(item_sku=row['SKU'], branch_id = store_id).count() > 0:
                return json.Response(f"Product sku {row['SKU']} already exist",200, False)
            if row['DESCRIPTION']=="":
                return json.Response(f"Product Code {row['PRODUCT CODE']} has no DESCRIPTION",200, True)
            if row['PRICE']=="":
                return json.Response(f"Product Code {row['PRODUCT CODE']} has no PRICE",200, True)
            if row['PRODUCT COUNT']=="":
                return json.Response(f"Product Code {row['PRODUCT CODE']} has no PRODUCT COUNT",200, True)
            if row['SALES TAX']=="":
                row['SALES TAX']=7.5
            
            try:
                price = float(row['PRICE'])
            except ValueError:
                return json.Response(f"Product Code {row['PRODUCT CODE']} price must be integer",200, True)

        row_iter = df.iterrows()
        for row in row_iter:
            item=ItemMstr(

                item_name = row[1]['NAME'],
                category_id = CategoryMstr.objects.get(category_name=row[1]['CATEGORY NAME']).id,
                sub_category = CategoryMstr.objects.get(category_name=row[1]['SUBCATEGORY NAME']),   
                item_description = row[1]['DESCRIPTION'],
            )
            item.save()
            
            branch=BranchItem(
                item=item,
                item_code = row[1]['PRODUCT CODE'],
                item_sku = row[1]['SKU'],
                item_price = price,
                item_tax = row[1]['SALES TAX'],
                item_count  = row[1]['PRODUCT COUNT'],
                item_discount_percent = 0.00,
                manager_id  = request.user.id,
                branch_id = BranchManager.objects.get(manager_id=request.user.id).branch_id,
                item_selling_price=0.00,
            )
            branch.save()
            
        return json.Response('Products uploaded Successfully',200, True)


class InventoryView(viewsets.ViewSet):
    @has_store_permission
    def add_product(self,request):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))
        
        item_name = datas['item_name']
        category_id = datas['category_name']
        sub_category = datas['subcategory_name']
        item_description = datas['item_description']
        item_image = datas['item_image']
        item_code = datas['item_code']
        item_sku = datas['item_sku']
        item_price = datas['item_price']
        item_tax = datas['item_tax']
        item_count = datas['item_count']

        branchitem_codecnt = BranchItem.objects.filter(item_code=item_code,branch_id  = BranchManager.objects.get(manager=request.user.id).branch_id).count()
        if branchitem_codecnt != 0:
            return json.Response("Product code already exist",200, False)
        branchitem_codecnt = BranchItem.objects.filter(item_sku=item_sku,branch_id  = BranchManager.objects.get(manager=request.user.id).branch_id).count()
        if branchitem_codecnt != 0:
            return json.Response("Product sku already exist",200, False)

        try:
            category=CategoryMstr.objects.get(category_name=category_id).id
        except CategoryMstr.DoesNotExist:
            return json.Response(f"No category name '{category_id}' exist",200, True)
        
        try:
            subcategory=CategoryMstr.objects.get(category_name=sub_category).parent_id
        except CategoryMstr.DoesNotExist:
            return json.Response(f"No subcategory name '{sub_category}' exist",200, True)

        if category != subcategory:
            return json.Response(f"Category name '{category_id}' have no subcategory '{sub_category}'",200, True)

        if item_image=="":
            item_image=None
        if item_tax=="":
            item_tax=7.5

        try:
            price = float(item_price)
        except ValueError:
            return json.Response("price must be integer",200, True)

        item=ItemMstr(
                item_name = item_name,
                category_id = CategoryMstr.objects.get(category_name=category_id).id,
                sub_category = CategoryMstr.objects.get(category_name=sub_category),   
                item_description = item_description,
                item_image = item_image,
            )
        item.save()
    
        branch=BranchItem(
            item=item,
            item_code = item_code,
            item_sku = item_sku,
            item_price = item_price,
            item_tax = item_tax,
            item_count  = item_count,
            item_discount_percent = 0.00,
            manager_id  = request.user.id,
            branch_id = BranchManager.objects.get(manager_id=request.user.id).branch_id,
            item_selling_price=0.00,
        )
        branch.save()

        return json.Response("Product Added Successfully",201, True)

    @has_store_permission
    def get_inventory_summary(self,request):
        
        branchmanager_id=BranchManager.objects.get(manager=request.user.id).branch_id
        item = BranchItem.objects.filter(branch_id=branchmanager_id,is_deleted=False).order_by('item_count')[:10]
        if request.method == 'GET':
            serializer = InventorySerializer(item, many=True)
            if serializer:
                return json.Response(serializer.data,200, True)

    @has_store_permission
    def get_products(self,request):
        try:
            branchmanager_id=BranchManager.objects.get(manager=request.user.id).branch_id
            item = BranchItem.objects.filter(branch_id=branchmanager_id,is_deleted=False).order_by('-id')
        except ObjectDoesNotExist:
            return json.Response("No item exist",404, False)

        if request.method == 'GET':
            serializer = InventorySerializer(item, many=True)
            if serializer:
                return json.Response(serializer.data,200, True)

    @has_store_permission
    def get_product(self,request,id):
        try:
            branchmanager_id=BranchManager.objects.get(manager=request.user.id).branch_id
            branchitem_id=ItemMstr.objects.get(id=id,is_deleted=False)
            item = BranchItem.objects.get(branch_id=branchmanager_id,item_id=branchitem_id,is_deleted=False)
        except ObjectDoesNotExist:
            return json.Response("No item exist",404, False)

        if request.method == 'GET':
            serializer = InventorySerializer(item)
            if serializer:
                return json.Response(serializer.data,200, True)

    @has_store_permission
    def update_product(self, request,id):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))

        item_name = datas['item_name']
        category_id = datas['category_name']
        sub_category = datas['subcategory_name']
        item_description = datas['item_description']
        item_image = datas['item_image']
        item_code = datas['item_code']
        item_sku = datas['item_sku']
        item_price = datas['item_price']
        item_tax = datas['item_tax']
        item_count = datas['item_count']
        
        try:
            branchitem = BranchItem.objects.get(manager_id=request.user.id,item_id=id,is_deleted=False)
        except ObjectDoesNotExist:
            return json.Response('You are not allowed to update this product',404, False)

        branchitem_codecnt = BranchItem.objects.filter(~Q(id=branchitem.id),item_code=item_code).count()
        if branchitem_codecnt > 0:
            return json.Response("Product id already exist",404, False)

        try:
            category=CategoryMstr.objects.get(category_name=category_id)
        except CategoryMstr.DoesNotExist:
            return json.Response(f"No category name '{category_id}' exist",200, True)
        
        try:
            subcategory=CategoryMstr.objects.get(category_name=sub_category)
        except CategoryMstr.DoesNotExist:
            return json.Response(f"No subcategory name '{sub_category}' exist",200, True)

        if category.id != subcategory.parent_id:
                return json.Response(f"Category name '{category_id}' have no subcategory '{sub_category}'",200, True)

        if item_image=="":
            item_image=None
        if item_tax=="":
            item_tax=7.5

        if request.method == 'PUT':
            itemtbl=ItemMstr.objects.filter(id=id).update(item_name=item_name,category_id=category.id,sub_category=subcategory,item_description=item_description,item_image=item_image)
            branchitemtbl=BranchItem.objects.filter(item_id=id).update(item_code=item_code,item_sku=item_sku,item_price=item_price,item_tax=item_tax,item_count=item_count,item_selling_price=item_price)

            return json.Response("Product Updated Successfully",200, True)
        return json.Response("Wrong method call",200, True)

    @has_store_permission
    def delete_product(self, request,id):

        try:
            branchmanager_id=BranchManager.objects.get(manager=request.user.id).branch_id
            item = BranchItem.objects.get(branch_id=branchmanager_id,item_id=id,is_deleted=False)
        except ObjectDoesNotExist:
            return json.Response('You are not allowed to delete this product',404, False)

        if request.method == 'DELETE':
            itemtbl=ItemMstr.objects.filter(id=id).update(is_deleted=True)
            branchitemtbl=BranchItem.objects.filter(item_id=id).update(is_deleted=True)

            return json.Response("Product Deleted Successfully",200, True)
        return json.Response("Wrong method call",200, True)

class SellerOrderView(viewsets.ViewSet):
    @has_store_permission
    def list_orders(self, request, *args, **kwargs):

        try:
            branch_id=BranchManager.objects.get(manager=request.user.id).branch_id
            orderstatus = "pending"
            orders = Order.objects.filter(store_id=branch_id, is_paid =True).exclude(order_status=orderstatus).order_by('-order_id')

        except ObjectDoesNotExist:
            return json.Response('Nothing to show',404, False)

        if request.method == "GET":
            serializer = OrderSerializer(orders,many=True).data
            
            for data in serializer:
                orderreport = OrderReport.objects.filter(order_id = data['order_id']).count()
                if orderreport > 0:
                    orderreport = OrderReport.objects.get(order_id = data['order_id']).feedback
                    data['report_feedback'] = orderreport
                else:
                    data['report_feedback'] = None  
            return json.Response(serializer,200, True)

    @has_store_permission
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
        else:
            return json.Response('Nothing to show',404, False)
            
    @has_store_permission
    def update_order_status(self, request):
    
        import json as j
        datas = j.loads(request.body.decode('utf-8'))
        order_id = datas['order_id']

        if 'order_status' in datas:
            order_status = datas['order_status']
        else:
            return json.Response("'Order status required",404, False)
        
        if order_status == "new" or order_status == "accepted" or order_status == "processing" or order_status == 'ready for pickup':
        	update_order_status = Order.objects.filter(order_id=order_id).update(order_status=order_status)

        if order_status == 'rejected':
            if 'reason' not in datas:
                return json.Response('Reason is Required',404, False)
            else:
                reason = datas['reason']
            update_order_status = Order.objects.filter(order_id=order_id).update(order_status=order_status,reason=datas['reason'])

        if order_status == 'completed':
        	update_order_status = Order.objects.filter(order_id=order_id).update(order_status=order_status, delivered_on = datetime.now())

        store_id = request.user.id
        
        branch_id = BranchManager.objects.get(manager_id = store_id).branch_id
        store_name = BranchMstr.objects.get(id = branch_id).branch_name
        store_address = BranchMstr.objects.get(id = branch_id).branch_address
        customer_id = Order.objects.get(order_id = order_id).customer_id
        customer_name = Profile.objects.get(id = customer_id).first_name
        cust_phone_no = Profile.objects.get(id = customer_id).phone_number

        if order_status == 'rejected':
            description = f"Your order {order_id} is {order_status},please find the reason in order summary"
        else:
        	description = f"Your order {order_id} is {order_status}"

        notification = Notification(
                order_id = order_id,
                store_id = store_id,
                customer_id = customer_id,
                title = 'order status updated',
                description = description,
                store_name = store_name,
                address = store_address,
                customer_name = customer_name,
                phone_no = cust_phone_no,
                order_status = order_status
            )
        notification.save()

        if order_status == 'completed': 
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

            get_customer_id = Order.objects.get(order_id = order_id).customer_id
            customer_email = Profile.objects.get(id = get_customer_id).email
            customer_placed_date = Order.objects.get(order_id = order_id).order_date
            delivered_on = Order.objects.get(order_id = order_id).delivered_on
            pickup_address = Profile.objects.get(id = get_customer_id).address

            context={
            "email":customer_email,
            "order_id":order_id,
            "placed_date":customer_placed_date,
            "delivered_date":delivered_on,
            "order_status":order_status,
            "pickup_address":pickup_address,
            "item_details":orderlist_seri,
            "cum":data
            }
            
            customer_subject = 'Your order completed'
            sendCustomMail(context, customer_email, customer_subject,'customer_order_delivered.html')
        return json.Response("Order Status updated successfully",200, True)
    
    @has_store_permission
    def update_timemanagement(self, request):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))

        order_id = datas['order_id']
        est_from_date = datas['est_from_date']
        est_start_time = datas['est_start_time']
        est_end_time = datas['est_end_time']
        order_status = "ready for pickup"
            
        update_time_status = Order.objects.filter(order_id=order_id).update(est_from_date=est_from_date,est_start_time=est_start_time,est_end_time=est_end_time)
        
        get_customer_id = Order.objects.get(order_id = order_id).customer_id
        customer_email = Profile.objects.get(id = get_customer_id).email
        customer_placed_date = Order.objects.get(order_id = order_id).order_date
        pickup_date = str(Order.objects.get(order_id = order_id).customer_from_date)
        prefer_pickup_date = pickup_date[:10]
        prefer_pickup_start_time = Order.objects.get(order_id = order_id).customer_start_time
        prefer_pickup_end_time = Order.objects.get(order_id = order_id).customer_end_time
        est_date = est_from_date[:10]

        context={
        "email":customer_email,
        "order_id":order_id,
        "placed_date":customer_placed_date,
        "prefer_pickup_date":prefer_pickup_date,
        "prefer_pickup_start_time":prefer_pickup_start_time,
        "prefer_pickup_end_time":prefer_pickup_end_time,
        "est_from_date":est_date,
        "est_start_time":est_start_time,
        "est_end_time":est_end_time,
        "order_status":order_status
        }

        customer_subject = 'Your order ready for pickup'
        sendCustomMail(context, customer_email, customer_subject,'order_status.html')

        return json.Response("Order Time Status updated successfully",200, True)
        
    @has_store_permission
    def get_order_status_count_based(self,request,*args, **kwargs):
        branch_id = BranchManager.objects.get(manager=request.user.id).branch_id
        orderstatus1 = Order.objects.filter(order_status='new',store_id=branch_id).order_by('-order_date')
        orderstatus2 = Order.objects.filter(order_status='completed',store_id=branch_id).order_by('-order_date')
        orderstatus3 = Order.objects.filter(order_status__in=['processing','accepted','ready for pickup'],store_id=branch_id).order_by('-order_date')

        if request.method == "GET":
            orderstatus1 = OrderSerializer(orderstatus1, many=True)
            orderstatus2 = OrderSerializer(orderstatus2, many=True)
            orderstatus3 = OrderSerializer(orderstatus3, many=True)
             
            return Response({
                'status':"OK",
                'message':'Order status list',
                'new':orderstatus1.data,
                'completed':orderstatus2.data,
                'processing':orderstatus3.data,
                'responseCode':status.HTTP_200_OK
            })

    @has_store_permission
    def get_order_status_count(self,request,*args, **kwargs):

        branch_id = BranchManager.objects.get(manager=request.user.id).branch_id

        orderstatus1 = Order.objects.filter(order_status='new',store_id=branch_id).count()
        orderstatus2 = Order.objects.filter(order_status='completed',store_id=branch_id).count()
        orderstatus3 = Order.objects.filter(order_status__in=['processing','accepted','ready for pickup'],store_id=branch_id).count()
        return Response({
                'status':"OK",
                'message':'Order status list',
                'new':orderstatus1,
                'completed':orderstatus2,
                'processing':orderstatus3,
                'responseCode':status.HTTP_200_OK
            })

    @has_store_permission
    def get_order_history(self,request,*args,**kwargs):

        try:
            branch_id = BranchManager.objects.get(manager=request.user.id).branch_id

            order_status = request.GET['status']

            if order_status == "new":
                current_user = Order.objects.filter(order_status='New',store_id=branch_id,is_paid =True).order_by('-order_id')
            if order_status == "rejected":
                current_user = Order.objects.filter(order_status='Rejected',store_id=branch_id,is_paid =True).order_by('-order_id')
            if order_status == "accepted":
                current_user = Order.objects.filter(order_status='Accepted',store_id=branch_id,is_paid =True).order_by('-order_id')
            if order_status == "processing":
                current_user = Order.objects.filter(order_status='Processing',store_id=branch_id,is_paid =True).order_by('-order_id')
            if order_status == "ready for pickup":
                current_user = Order.objects.filter(order_status='Ready for Pickup',store_id=branch_id,is_paid =True).order_by('-order_id')
            if order_status == "completed":
                current_user = Order.objects.filter(order_status='Completed',store_id=branch_id,is_paid =True).order_by('-order_id')
            if order_status == "incomplete":
                current_user = Order.objects.filter(order_status='Incomplete',store_id=branch_id,is_paid =True).order_by('-order_id')
            if order_status == "refund issued":
                current_user = Order.objects.filter(order_status='Refund Issued',store_id=branch_id,is_paid =True).order_by('-order_id')
            if order_status == "pending":
                current_user = Order.objects.filter(order_status='Pending',store_id=branch_id,is_paid = False).order_by('-order_id')
           
            if order_status == "all":
                current_user = Order.objects.filter(store_id=branch_id).exclude(payment_type=None).order_by('-order_id')
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
        
@csrf_exempt
def StoreForgetPassword(request):
    import json as j
    if request.method == 'POST':
        
        data = request.POST
        email = data['email']

        if 'email' not in data:
            return json.Response('Email Address is Required',404, False)

        try:
            user = Profile.objects.get(email=email,is_active=True,is_store=True)
            token = get_tokens_for_user(user)
            time=datetime.now()+timedelta(hours=2)
            serializer = ResetTokenSerializer(
                data={'user': user.id, 'jwt_token': token['access'],'expire_ts': time})
            if serializer.is_valid():
                serializer.save()
            name = Profile.objects.get(email = email).first_name

            context = {
                'email': email,
                'name': name,
                'reset_password_url': "http://13.233.62.76:3000/auth/reset-password/" + token['access'],
            }

            subject = "Reset Password"
            recepiants = email

            sendCustomMail(context, recepiants, subject,'storereset_password.html')
            return json.Response('Email_Sent',200, True)
        except:
            return json.Response('No_User_Found',200, False)

class CustomerListAPIView(viewsets.ViewSet):
    @has_store_permission
    def get_customers_list(self, request):

        try:
            customer = Profile.objects.filter(is_customer=True,is_active=True).order_by('-id')
        except Profile.DoesNotExist:
            return json.Response("No customer found",404, False)

        if request.method == 'GET':
            serializer = CustomerSerializer(customer, many=True)
            if serializer:
                return json.Response(serializer.data,200, True)

class DiscountAPIView(viewsets.ViewSet):
    @has_store_permission
    def discount_update(self,request,item_code):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))
        item_code = datas['item_code']
        item_price = datas['item_price']
        discounted_price = datas['item_discount_percent']
        
        output = float(item_price) - float(discounted_price)
       
        try:
            branch = BranchItem.objects.filter(item_code=item_code,manager_id=request.user.id).update(item_price=item_price,item_selling_price=discounted_price,item_discount_percent=output)
            return json.Response("Product discount updated Successfully",200, True)
        except Exception as e:
            return json.Response("Unable to update",404, False)
            
class NotificationListAPIView(viewsets.ViewSet):
    @has_store_permission
    def get_notification_list(self, request):

        try:
            branch_id = BranchManager.objects.get(manager=request.user.id).branch_id
            notification = Notification.objects.filter(store_id=branch_id).order_by('-id')
            read = Notification.objects.filter(store_id=branch_id,is_read=False).values_list('id',flat=True)
            
            for data in read:
                user_id = Notification.objects.filter(id=data).update(is_read=True)

        except Profile.DoesNotExist:
            return json.Response("No notification found",404, False)

        if request.method == 'GET':
            serializer = NotificationSerializer(notification, many=True)
            if serializer:
                return Response({
                'status':"OK",
                'data' :serializer.data,
                'responseCode':status.HTTP_200_OK
            })       

    @has_store_permission
    def get_notification_count(self, request):

        try:
            branch_id = BranchManager.objects.get(manager=request.user.id).branch_id
            unread = Notification.objects.filter(store_id=branch_id, is_read = False).count()
            
        except Profile.DoesNotExist:
            return json.Response("No notification found",404, False)
        if request.method == 'GET':
            if unread >= 0:
                count = unread
            
            return json.Response(count,200, True)

    @has_store_permission         
    def delete_notification(self, request):
        import json as j
        datas = j.loads(request.body.decode('utf-8'))
        delete_id = datas['delete_id']
        for map in delete_id:
            try:
                branch_id = BranchManager.objects.get(manager=request.user.id).branch_id
                notification = Notification.objects.filter(id=map,store_id=branch_id).delete()
            except Notification.DoesNotExist:
                return json.Response('Nothing to show',404,False)
            
        return json.Response('Successfully deleted',200, True)

class ImageAPIView(viewsets.ViewSet):
    @has_store_permission
    def image_upload(self, request):
        import json as j
        datas = j.loads(request.body.decode('utf-8'))
        item_id = datas['item_id']
        for image in datas['images']:
        # itemimage = Image()
            image=Image(
                item_id=item_id,
                image= image
            )
            image.save()
        return json.Response('Image uploaded successfully',200, True)
        
