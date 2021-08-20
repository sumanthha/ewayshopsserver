from django.db.models.query_utils import Q
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers import *
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action, api_view
from users.permission import has_permission, has_admin_permission
from django.shortcuts import get_object_or_404
from ewayshop.settings import SECRET_KEY
from ewayshop import settings
from . import json
from django.views.decorators.csrf import csrf_exempt
from time import sleep, time
from django.utils import timezone
from django.contrib.auth.hashers import make_password,check_password
from django.views.generic import View
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
# from users.notification import send_notification
from rest_framework_simplejwt import authentication
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from users.helper import *
import pytz
import pandas as pd
import numpy as np
from django.core.exceptions import ObjectDoesNotExist


class MyObtainTokenPairView(TokenObtainPairView):
    authentication_classes  = [authentication.JWTTokenUserAuthentication]
    serializer_class        = MyTokenObtainPairSerializer
    permission_classes      = (AllowAny,)
    queryset                = Profile.objects.all()
    

    def post(self, request, *args, **kwargs):
        data = request.data
        if 'email' not in data:
            return json.Response('Email Address is Required',404, False)
        else:
            email = data.get('email')

        if 'password' not in data:
            return json.Response('Password is Required',404, False)
        else:
            password = data.get('password')

        try:
            login_user = Profile.objects.get(email=email)
        except Profile.DoesNotExist:
            return Response({
                'status': "Error",
                'message': 'Please enter the valid email',
                'responseCode': status.HTTP_404_NOT_FOUND
            })
        
        try:
            active_user = Profile.objects.get(email=email,is_active=True)
        except Profile.DoesNotExist:
            return Response({
                'status': "ok",
                'message': 'Inactive account please contact admin',
                'responseCode': status.HTTP_404_NOT_FOUND
            })
        
        if Profile.objects.filter(email=email,password = None).count() > 0: 
        
            return Response({
                'status': "Error",
                'message': 'We have sent an email with reset password link to your email address . please reset your password.',
                'responseCode': status.HTTP_404_NOT_FOUND
            })
    
        if check_password(request.POST['password'], login_user.password):
            
            response = {"detail": "Invalid credentials"}
            user = Profile.objects.filter(email=email, password=password)
            if (user != None):

                serializer = self.get_serializer(data=request.data)
                response = serializer.validate(request.data)
            else:
                
                response = {"detail": "Invalid credentials"}
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
            return Response(response, status=status.HTTP_201_CREATED)
        return Response({
            'status': "Error",
            'message': 'Incorrect password',
            'responseCode': status.HTTP_404_NOT_FOUND
        })

class UsersProfileDetails(viewsets.ViewSet):
    @has_admin_permission
    def get_bussiness_admin(self, request, *args, **kwargs):
        try:
            user = self.request.user
            current_user = Profile.objects.get(email=user)
        except Profile.DoesNotExist:
            return Response({
                'status': "Error",
                'message': 'Nothing to show',
                'responseCode': status.HTTP_404_NOT_FOUND
            })

        if request.method == "GET":
            serializer = BussinessAdminSerializer(current_user)
            return Response({
                'status': "OK",
                'message': 'Content is listed',
                'data': serializer.data,
                'responseCode': status.HTTP_200_OK
            })

    @has_admin_permission
    def update_bussiness_admin(self, request):
        try:
            user = Profile.objects.get(id=request.user.id)
        except Profile.DoesNotExist:
            return Response({
                'status': "Error",
                'message': 'Nothing to update',
                'responseCode': status.HTTP_404_NOT_FOUND
            })

        if request.method == "PUT":
            serializer = BussinessAdminSerializer(user, data=request.data)
            data = {}
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': "OK",
                    'message': 'Profile Updated Successfully',
                    'responseCode': status.HTTP_200_OK
                })
            return Response({
                'status': "Error",
                'message': serializer.errors,
                'responseCode': status.HTTP_404_NOT_FOUND
            })


class SignUpView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SignUpView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))
        address = datas['address']
        first_name = datas['first_name']
        group = datas['group']
        last_name = datas['last_name']
        phone_number = datas['phone_number']
        landmark = datas['landmark']
        gender = datas['gender']
        photo = datas['photo']
        latitude = datas['latitude']
        longitude = datas['longitude']

        if 'email' not in datas:
            return json.Response('Email Address is Required',404, False)
        else:
            email = datas['email']
        if 'password' not in datas:
            return json.Response('Password is Required',404, False)
        else:
            password = datas['password']

        user = Profile.objects.filter(email=email).count()
        if user == 0:
            usertbl = Profile(email=email, 
            address=address,
            first_name=first_name, 
            last_name=last_name, 
            phone_number=phone_number, 
            landmark=landmark,
            gender=gender,
            photo=photo,
            latitude=latitude,
            longitude=longitude,
            is_customer=True, 
            password=make_password(password))
            usertbl.save()

            group = Group.objects.get(name=group)

            group = UserGroup(user=usertbl, group=group)
            group.save()

        else:
            return json.Response("Email already exist",200, False)

        return json.Response("User created Successfully",201, True)

class CreateRequestBranch(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateRequestBranch, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))
        branch_code = datas['branch_code']
        branch_name = datas['branch_name']
        branch_email = datas['branch_email']
        branch_description = datas['branch_description']
        branch_address = datas['branch_address']
        latitude = datas['latitude']
        longitude = datas['longitude']
        zipcode = datas['zipcode']
        branch_phone = datas['branch_phone']

        if 'branch_code' not in datas:
            return json.Response('branch email Address is Required',404, False)
        else:
            branch_email = datas['branch_email']

        code = BranchMstr.objects.filter(branch_code=branch_code).count()
        if code == 0:
            pass
        else:
            return json.Response("branch code already exist",200, False)

        branch = BranchMstr.objects.filter(branch_email=branch_email).count()
        if branch == 0:
            usertbl = BranchMstr(branch_code=branch_code, 
            branch_name=branch_name,
            branch_email=branch_email, 
            branch_description=branch_description, 
            branch_address=branch_address, 
            latitude=latitude,
            longitude=longitude,
            zipcode=zipcode,
            branch_phone=branch_phone)
            
            usertbl.save()

        else:
            return json.Response("Branch email already exist",200, False)

        return json.Response("Branch Request Sent Successfully",201, True)


class Branch(viewsets.ViewSet):
    @has_admin_permission
    def create_branch_admin(self, request):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))
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
        branch_email = datas['branch_email']
        branch_description = datas['branch_description']
        branch_address = datas['branch_address']
        latitude = datas['latitude']
        longitude = datas['longitude']
        zipcode = datas['zipcode']
        branch_phone = datas['branch_phone']
        is_active=True

        if 'branch_email' not in datas:
            return json.Response('branch email Address is Required',404, False)
        else:
            branch_email = datas['branch_email']
 
        branch_count = BranchMstr.objects.filter(branch_name=branch_name).count()
        if branch_count != 0:
            return json.Response("branch name already exist",200, False)

        branch = BranchMstr.objects.filter(branch_email=branch_email).count()
        if branch == 0:
            usertbl = BranchMstr(branch_code=branch_code, 
            branch_name=branch_name,
            branch_email=branch_email, 
            branch_description=branch_description, 
            branch_address=branch_address, 
            latitude=latitude,
            longitude=longitude,
            zipcode=zipcode,
            branch_phone=branch_phone,
            is_active=is_active)
            usertbl.save()

        else:
            return json.Response("Branch email already exist",200, False)

        return json.Response("Branch Created Successfully",201, True)

    @has_admin_permission
    def get_branches_admin(self, request):
        try:
            branch = BranchMstr.objects.filter(is_active=True)
        except BranchMstr.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = BranchSerializer(branch, many=True)
            if serializer:
                return Response({
                    'status': "OK",
                    'message': 'Content is listed',
                    'data': serializer.data,
                    'responseCode': status.HTTP_200_OK
                })

    @has_admin_permission
    def get_branche_admin(self, request,branch_code):
        try:
            branch = BranchMstr.objects.get(branch_code=branch_code,is_active=True)
        except BranchMstr.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = BranchSerializer(branch)
            if serializer:
                return Response({
                    'status': "OK",
                    'message': 'Content is listed',
                    'data': serializer.data,
                    'responseCode': status.HTTP_200_OK
                })

    @has_permission
    def update_branch_admin(self, request,branch_code):
        try:
            branch = BranchMstr.objects.get(branch_code=branch_code,is_active=True)
        except BranchMstr.DoesNotExist:
            return Response({
                'status': "Error",
                'message': 'Nothing to update',
                'responseCode': status.HTTP_404_NOT_FOUND
            })

        if request.method == "PUT":
            serializer = BranchUpdateSerializer(branch, data=request.data)
            data = {}
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': "OK",
                    'message': 'Branch is Updated Successfully',
                    'responseCode': status.HTTP_200_OK
                })
            return Response({
                'status': "Error",
                'message': serializer.errors,
                'responseCode': status.HTTP_404_NOT_FOUND
            })

    @has_admin_permission
    def delete_branch_admin(self, request, branch_code, *args, **kwargs):
        try:
            branch = BranchMstr.objects.get(branch_code=branch_code,is_active=True)
        except BranchMstr.DoesNotExist:
            return Response({
                'status': "Error",
                'message': 'Nothing to Delete',
                'responseCode': status.HTTP_404_NOT_FOUND
            })

        if request.method == 'DELETE':

            check = BranchManager.objects.filter(branch=branch.id).count()
            if check==0:

                branch_delete = BranchMstr.objects.filter(branch_code=branch_code).update(is_active=False)
                return Response({
                    'status': "OK",
                    'message': 'Branch is Deleted Successfully',
                    'responseCode': status.HTTP_200_OK
                })
            return Response({
                    'status': "OK",
                    'message': f"Can't delete, {check} Branch manager exist",
                    'responseCode': status.HTTP_200_OK
                })


class BranchManagerView(viewsets.ViewSet):
    @has_admin_permission
    def create_branch_manager(self, request):
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
        first_name = datas['first_name']
        last_name = datas['last_name']
        phone_number = datas['phone_number']
        email= datas['email']
        address= datas['address']
        landmark= datas['landmark']
        latitude=datas['latitude']
        longitude=datas['longitude']
        branch_code=datas['branch_code']
        group = datas['group']
        
        if 'email' not in datas:
            return json.Response('Email Address is Required',404, False)
        else:
            email = datas['email']
        if 'password' not in datas:
            return json.Response('Password is Required', False)
        else:
            given_password = datas['password']
        
        try:
            branch = BranchMstr.objects.get(branch_code=branch_code,is_active=True)
        except BranchMstr.DoesNotExist:
            return Response({
                'status': "Error",
                'message': 'Invalid branch',
                'responseCode': status.HTTP_404_NOT_FOUND
            })

        user = Profile.objects.filter(email=email).count()
        if user == 0:
            usertbl = Profile(profile_code=profile_code,
            email=email,
            password=make_password(given_password),
            address=address,
            first_name=first_name, 
            last_name=last_name, 
            phone_number=phone_number, 
            landmark=landmark,
            latitude=latitude,
            longitude=longitude,
            is_store=True)
            usertbl.save()
            branch_map = BranchManager(manager=usertbl,branch=branch)
            branch_map.save()
            group = Group.objects.get(name=group)
            group = UserGroup(user=usertbl, group=group)
            group.save()

            context = {
                    'first_name':first_name,
                    'email': email,
                    'password': given_password,
                }

            subject = "Welcome to eWayShops"
            recepiants = email

            sendCustomMail(context, recepiants, subject,'admin_send_details.html')

        else:
            return json.Response("Email already exist",200, False)

        return json.Response("Branch manager created Successfully",201, True)

    @has_admin_permission
    def get_branch_managers_admin(self, request):
        try:
            profile = Profile.objects.filter(is_store=True)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = ManagerProfileSerializer(profile, many=True)
            if serializer:
                return Response({
                    'status': "OK",
                    'message': 'Content is listed',
                    'data': serializer.data,
                    'responseCode': status.HTTP_200_OK
                })

    @has_admin_permission
    def get_branch_manager_admin(self, request,profile_code):
        try:
            branch = Profile.objects.get(profile_code=profile_code)
        except BranchMstr.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = ManagerProfileSerializer(branch)
            if serializer:
                return Response({
                    'status': "OK",
                    'message': 'Content is listed',
                    'data': serializer.data,
                    'responseCode': status.HTTP_200_OK
                })

  
    def update_branch_manager_admin(self, request,profile_code):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))
        branch_name = datas['branch_name']
        try:
            manager = Profile.objects.get(profile_code=profile_code)
        except Profile.DoesNotExist:
            return json.Response('Nothing to update',404, False)
        try:
            branch = BranchMstr.objects.get(branch_name=branch_name)
        except BranchMstr.DoesNotExist:
            return json.Response('Invalid Branch',404, False)

        if request.method == "PUT":
            serializer = BranchManagerUpdateSerializer(manager, data=request.data)
            if serializer.is_valid():
                serializer.save()
                manager = BranchManager.objects.filter(manager=manager.id).update(branch=branch)
                return json.Response('Branch manager is Updated Successfully',200, True)
            return json.Response(serializer.errors,200, False)

    @has_admin_permission
    def delete_branch_manager_admin(self, request, profile_code, *args, **kwargs):
        try:
            manager = Profile.objects.get(profile_code=profile_code)
        except Profile.DoesNotExist:
            return Response({
                'status': "Error",
                'message': 'Nothing to Delete',
                'responseCode': status.HTTP_404_NOT_FOUND
            })

        if request.method == 'DELETE':
            if manager.is_active == True:
                check = BranchManager.objects.filter(manager=manager.id).update(is_active = False)
                buyer = Profile.objects.filter(profile_code=profile_code).update(is_active=False)
                message = "Branch manger is deactivated"
            else:
                check = BranchManager.objects.filter(manager=manager.id).update(is_active = True)
                buyer = Profile.objects.filter(profile_code=profile_code).update(is_active=True)
                message = "Branch manger is activated"
            return Response({
                'status': "OK",
                'message': message,
                'responseCode': status.HTTP_200_OK
            })

class CategoryView(viewsets.ViewSet):
    @has_admin_permission
    def create_category(self, request):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))
        category_code = datas['category_code']
        category_name = datas['category_name']

        categorynm = CategoryMstr.objects.filter(category_name=category_name).count()
        if categorynm != 0:
            return json.Response("category name already exist",200, False)
        category = CategoryMstr.objects.filter(category_code=category_code).count()
        if category == 0:
            categorytbl = CategoryMstr(category_code=category_code, 
            category_name=category_name)
            categorytbl.save()

        else:
            return json.Response("category code already exist",200, False)

        return json.Response("category created Successfully",201, True)

    @has_permission
    def get_categories(self, request):
        try:
            category = CategoryMstr.objects.filter(is_deleted=False,parent_id=0)
        except CategoryMstr.DoesNotExist:
            return json.Response("No category exist", False)

        if request.method == 'GET':
            serializer = CategorySerializer(category, many=True)
            if serializer:
                return Response({
                    'status': "OK",
                    'message': 'Content is listed',
                    'data': serializer.data,
                    'responseCode': status.HTTP_200_OK
                })

    @has_admin_permission
    def get_category(self, request,category_code):

        try:
            category = CategoryMstr.objects.get(category_code=category_code,is_deleted=False,parent_id=0)
        except CategoryMstr.DoesNotExist:
            return json.Response("No category exist",404, False)

        if request.method == 'GET':
            serializer = CategorySerializer(category)
            if serializer:
                return Response({
                    'status': "OK",
                    'message': 'Content is listed',
                    'data': serializer.data,
                    'responseCode': status.HTTP_200_OK
                })
  
    def update_category(self, request,category_code):
        import json as j
        datas = j.loads(request.body.decode('utf-8'))
        try:
            category = CategoryMstr.objects.get(category_code=category_code,is_deleted=False,parent_id=0)
        except CategoryMstr.DoesNotExist:
            return json.Response("No category exist",400, True)

        if request.method == "PUT":
            serializer = CategorySerializer(category, data=request.data)
            category_count = CategoryMstr.objects.filter(~Q(category_code=category_code), category_name=datas['category_name']).count()
            if category_count > 0:
                return json.Response("Category name already exist",400, True)
            if serializer.is_valid():
                serializer.save()
                return json.Response('Category is Updated Successfully',200, True)
            return json.Response("Category already exist",400, True)

    @has_admin_permission
    def delete_category(self, request, category_code, *args, **kwargs):
        try:
            category = CategoryMstr.objects.get(category_code=category_code,parent_id=0)
        except CategoryMstr.DoesNotExist:
            return json.Response("No category exist",404, False)
        parent = CategoryMstr.objects.filter(parent_id=category.id,is_deleted=False).count()

        if parent > 0:
            return json.Response(f"Can't delete, {parent} subcategory exist",200, True)
        category_id = category.id
        if category_id > 0:
            item_count = ItemMstr.objects.filter(category_id = category_id).count()
            if item_count > 0:
                item_id = ItemMstr.objects.get(category_id = category_id).id
                branch_id = BranchItem.objects.get(item_id = item_id).branch_id
                return json.Response(f"Can't delete, {category_id} is mapped with {branch_id}",200, True)
            else:
                catdel = CategoryMstr.objects.filter(category_code=category_code).update(is_deleted=True)
                delete_category = CategoryMstr.objects.get(category_code=category_code).delete()
                return Response({
                    'status': "OK",
                    'message': 'category is Deleted Successfully',
                    'responseCode': status.HTTP_200_OK
                })

    @has_admin_permission
    def category_bulk_upload(self, request):
        import os
        document = request.FILES['csv']
        file_extension = os.path.splitext(document.name)[1]
        
        if file_extension != ".csv":
            return json.Response('Invalid file format',200, False)
        df = pd.read_csv(document,sep=',').replace(np.nan, "",regex=True).replace("\t", '', regex=True)

        if (list(df.columns)[0]) == "Unnamed: 0":
            return json.Response("Column name is missing",200, True)
        if (list(df.columns)[1]) == "Unnamed: 1":
            return json.Response("Column name is missing",200, True)
        if (list(df.columns)[0]) != "CATEGORY CODE":
            return json.Response(f"Invalid column name {(list(df.columns)[0])}",200, True)
        if (list(df.columns)[1]) != "CATEGORY NAME":
            return json.Response(f"Invalid column name {(list(df.columns)[1])}",200, True)
        filter=np.logical_or(df["CATEGORY NAME"] != "", df["CATEGORY CODE"] != "")

        df = df[filter]
        row_iter = df.iterrows()
        var = []
        for  index,row in row_iter:
            
            if CategoryMstr.objects.filter(category_code=row['CATEGORY CODE']).count() != 0:
                return json.Response(f"Category code {row['CATEGORY CODE']} already exist",200, True)
            if CategoryMstr.objects.filter(category_name=row['CATEGORY NAME']).count() != 0:
                return json.Response(f"Category name {row['CATEGORY NAME']} already exist",200, True)
            if row['CATEGORY CODE']=="":
                return json.Response(f"Category name {row['CATEGORY NAME']} has no Category code",200, True)
            if row['CATEGORY NAME']=="":
                return json.Response(f"Category {row['CATEGORY CODE']} has no Category name",200, True)
            if row['CATEGORY NAME'] in var:
                return json.Response(f"Category {row['CATEGORY CODE']} has no Category name",200, True)
            var.append(row['CATEGORY NAME'])

        row_iter = df.iterrows()
        for  index,row in row_iter:
            
            categorytbl=CategoryMstr(

                category_code = row['CATEGORY CODE'],

                category_name  = row['CATEGORY NAME']

            )
            categorytbl.save()
        return json.Response('Category uploaded Successfully',200, True)


class SubCategoryView(viewsets.ViewSet):
    @has_admin_permission
    def create_subcategory(self, request):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))
        category_code = datas['category_code']
        category_name = datas['category_name']
        parent_name = datas['parent_name']
        try:
            category = CategoryMstr.objects.get(category_code=parent_name,is_deleted=False)
        except CategoryMstr.DoesNotExist:
            return json.Response("No category exist",404, False)
        parent_id=category.id
        categorynm = CategoryMstr.objects.filter(category_name=category_name).count()
        if categorynm != 0:
            return json.Response("Subcategory name already exist",200, False)
        category = CategoryMstr.objects.filter(category_code=category_code).count()
        if category == 0:
            categorytbl = CategoryMstr(category_code=category_code, 
            category_name=category_name,parent_id=parent_id)
            categorytbl.save()

        else:
            return json.Response("Subcategory code already exist",200, False)

        return json.Response("Subcategory created Successfully",201, True)

    @has_admin_permission
    def get_subcategories(self, request):
        try:
            subcategory = CategoryMstr.objects.filter(parent_id__gt=0,is_deleted=False)
        except CategoryMstr.DoesNotExist:
            return json.Response("No subcategory exist",404, False)

        if request.method == 'GET':
            serializer = SubCategorySerializer(subcategory, many=True)
            if serializer:
                return Response({
                    'status': "OK",
                    'message': 'Content is listed',
                    'data': serializer.data,
                    'responseCode': status.HTTP_200_OK
                })

    @has_admin_permission
    def get_subcategory(self, request,category_code):
        try:
            category = CategoryMstr.objects.get(category_code=category_code,is_deleted=False,parent_id__gt=0)
        except CategoryMstr.DoesNotExist:
            return json.Response("No category exist",404, False)

        if request.method == 'GET':
            serializer = SubCategorySerializer(category)
            if serializer:
                return Response({
                    'status': "OK",
                    'message': 'Content is listed',
                    'data': serializer.data,
                    'responseCode': status.HTTP_200_OK
                })

    @has_admin_permission
    def update_subcategory(self, request,category_code):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))
        parent_name = datas['parent_name']
        try:
            parent = CategoryMstr.objects.get(category_code=category_code,is_deleted=False,parent_id__gt=0)
        except Profile.DoesNotExist:
            return json.Response('Nothing to update',404, False)

        subcategory_count = CategoryMstr.objects.filter(~Q(category_code=category_code), category_name=datas['category_name']).count()
        if subcategory_count > 0:
            return json.Response("Subcategory name already exist",200, False)
        count = CategoryMstr.objects.filter(~Q(id=parent.id), category_code=datas['category_code']).count()
        if count > 0:
            return json.Response("Subcategory code already exist",200, False)
        try:
            category = CategoryMstr.objects.get(category_code=parent_name,is_deleted=False)
        except CategoryMstr.DoesNotExist:
            return json.Response("No category exist",404, False)

        if request.method == "PUT":
            serializer = SubCategorySerializer(parent, data=request.data)
            if serializer.is_valid():
                serializer.save()
                update = CategoryMstr.objects.filter(id=parent.id).update(parent_id=category.id)
                return json.Response('subcategory is Updated Successfully',201, True)
            return json.Response(serializer.errors, False)


    @has_admin_permission
    def delete_subcategory(self, request, category_code, *args, **kwargs):
        try:
            category = CategoryMstr.objects.get(category_code=category_code,parent_id__gt=0)
        except CategoryMstr.DoesNotExist:
            return json.Response("No subcategory exist",404, False)

        if request.method == 'DELETE':
            catdel = CategoryMstr.objects.filter(category_code=category_code).update(is_deleted=True)
            return Response({
                'status': "OK",
                'message': 'subcategory is Deleted Successfully',
                'responseCode': status.HTTP_200_OK
            })

    @has_admin_permission
    def subcategory_bulk_upload(self, request):
        import os
        document = request.data.get('csv')
        file_extension = os.path.splitext(document.name)[1]
        if file_extension != ".csv":
            return json.Response('Invalid file format',200, False)
        df = pd.read_csv(document,sep=',').replace(np.nan, '',regex=True).replace("\t", '', regex=True)

        if (list(df.columns)[0]) == "Unnamed: 0":
            return json.Response("Column name is missing",200, True)
        if (list(df.columns)[1]) == "Unnamed: 1":
            return json.Response("Column name is missing",200, True)
        if (list(df.columns)[2]) == "Unnamed: 2":
            return json.Response("Column name is missing",200, True)
        if (list(df.columns)[0]) != "SUBCATEGORY CODE":
            return json.Response(f"Invalid column name {(list(df.columns)[0])}",200, True)
        if (list(df.columns)[1]) != "SUBCATEGORY NAME":
            return json.Response(f"Invalid column name {(list(df.columns)[1])}",200, True)
        if (list(df.columns)[2]) != "CATEGORY CODE":
            return json.Response(f"Invalid column name {(list(df.columns)[2])}",200, True)
        filter=np.logical_or(df["SUBCATEGORY CODE"] != "", df["CATEGORY CODE"] != "")
        df = df[filter]
        row_iter = df.iterrows()

        for index, row in row_iter:

            if CategoryMstr.objects.filter(category_code=row['SUBCATEGORY CODE']).count() != 0:
                return json.Response(f"Subcategory code {row['SUBCATEGORY CODE']} already exist",200, True)
            if CategoryMstr.objects.filter(category_name=row['SUBCATEGORY NAME']).count() != 0:
                return json.Response(f"Subcategory name {row['SUBCATEGORY NAME']} already exist",200, True)
            if row['SUBCATEGORY CODE']=="":
                return json.Response(f"Subcategory name {row['SUBCATEGORY NAME']} has no Subcategory code",200, True)
            if row['SUBCATEGORY NAME']=="":
                return json.Response(f"Subcategory code {row['SUBCATEGORY CODE']} has no Subcategory name",200, True)
            if row['CATEGORY CODE']=="":
                return json.Response("Category Code should not be empty",200, True)
            if CategoryMstr.objects.filter(category_code=row['CATEGORY CODE']).count() == 0:
                return json.Response(f"Invalid Category Code {row['CATEGORY CODE']}",200, True)

        row_iter = df.iterrows()
        for index, row in row_iter:
            subcategorytbl=CategoryMstr(

                category_code = row['SUBCATEGORY CODE'],

                category_name  = row['SUBCATEGORY NAME'],

                parent_id  = CategoryMstr.objects.get(category_code=row['CATEGORY CODE']).id

            )
            subcategorytbl.save()
            
            
        return json.Response('Subcategory uploaded Successfully',200, True)

class CommissionView(viewsets.ViewSet):
    @has_admin_permission
    def create_commission(self, request):
        import json as j

        datas = j.loads(request.body.decode('utf-8'))
        group_code = datas['group_code']
        name = datas['name']
        description = datas['description']
        percentage = datas['percentage']
        branchs = datas['branch']
        commission = Commission.objects.filter(group_code=group_code).count()
        if commission > 0:
            return json.Response("commission group code already exist",200, False)
        for branch in branchs:
            try:
                branchtbl=BranchMstr.objects.get(branch_code=branch['branch_code'],is_active=True)
            except BranchMstr.DoesNotExist:	
                return json.Response(f"invalid branch code {branch['branch_code']}",200, False)
          
            if CommissionMapping.objects.filter(branch_id=branchtbl.id).count()>0:
                return json.Response(f"{branchtbl.branch_name} already Mapped",200, False)

        commissiontbl = Commission(group_code=group_code, 
        name=name,description=description,percentage=percentage)
        commissiontbl.save()
        branchs = datas['branch']
        for branch in branchs:
            branchcommission_instance = CommissionMapping()
            branchcommission_instance.branch = BranchMstr.objects.get(branch_code=branch['branch_code'])
            branchcommission_instance.commission=Commission.objects.get(id=commissiontbl.id)
            branchcommission_instance.save()

            
        return json.Response("commission created Successfully",201, True)

    @has_admin_permission
    def get_commissions(self, request):

        try:
            commission = Commission.objects.filter(is_deleted=False)
        except Commission.DoesNotExist:
            return json.Response("No Commission exist",404, False)

        if request.method == 'GET':
            serializer = CommissionSerializer(commission, many=True)
            if serializer:
                return json.Response(serializer.data,200, True)

    @has_admin_permission
    def get_commission(self, request,group_code):
        try:
            commission = Commission.objects.get(group_code=group_code,is_deleted=False)
        except Commission.DoesNotExist:
            return json.Response("No Commission exist",404, False)

        if request.method == 'GET':
            serializer = CommissionMapSerializer(commission)
            if serializer:
                return json.Response(serializer.data,200, True)

    @has_admin_permission
    def update_commission(self, request, group_code):
        data = request.data
        obj = Commission.objects.get(group_code=group_code,is_deleted=False)
        serializer = CommissionSerializer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            branchs = data['branch']
            remove_map=CommissionMapping.objects.filter(commission_id=obj.id).delete()
            for branch in branchs:
                try:
                    branchtbl=BranchMstr.objects.get(branch_code=branch['branch_code'],is_active=True)
                except BranchMstr.DoesNotExist:	
                    return json.Response(f"invalid branch code {branch['branch_code']}",200, False)
            
                if CommissionMapping.objects.filter(branch_id=branchtbl.id).count()>0:
                    return json.Response(f"{branchtbl.branch_name} already Mapped",200, False)
                branchs = data['branch']
            for branch in branchs:

                branchcommission_instance = CommissionMapping()
                branchcommission_instance.branch = BranchMstr.objects.get(branch_code=branch['branch_code'])
                branchcommission_instance.commission=Commission.objects.get(id=obj.id)
                branchcommission_instance.save()

            return json.Response("commission updated Successfully" ,200, True)
        else:
            return json.Response(serializer.errors,200, False)


    @has_admin_permission
    def delete_commission(self, request, group_code, *args, **kwargs):
        try:
            commission = Commission.objects.get(group_code=group_code)
        except Commission.DoesNotExist:
            return json.Response("No Commission exist",404, False)
        mapped = CommissionMapping.objects.filter(commission_id=commission.id).count()
        if mapped != 0:
            return json.Response(f"Can't delete {mapped}, Already mapped",200, True)

        if request.method == 'DELETE':
            comdel = Commission.objects.filter(group_code=group_code).update(is_deleted=True)
            return json.Response('Commission is Deleted Successfully',200, True)


    @has_admin_permission	
    def commission_mapping(self, request,group_code, *args, **kwargs):
        import json as j	
        datas = j.loads(request.body.decode('utf-8'))
        branch = datas['branch']
        try:
            commission=Commission.objects.get(group_code=group_code,is_deleted=False)
        except Commission.DoesNotExist:	
            return json.Response("Comission not found",404, False)	
        for x in branch:
            try:
                branchtbl=BranchMstr.objects.get(branch_code=x,is_active=True)
            except BranchMstr.DoesNotExist:	
                return json.Response(f"invalid branch code {x}",200, False)
            branchchk=CommissionMapping.objects.filter(branch_id=branchtbl.id).count()
            if branchchk !=0:
                return json.Response(f'{branchtbl.branch_name} is already mapped',200, True)
            commissiontbl = CommissionMapping(commission_id=commission.id, 	
            branch_id=branchtbl.id)	
            commissiontbl.save()
        return json.Response('Commission mapped Successfully',200, True)

    @has_admin_permission	
    def Unmapped_list(self, request,group_code,*args, **kwargs):

        if group_code == 'new':
            try:
                commission=BranchMstr.objects.exclude(id__in=CommissionMapping.objects.values_list('branch_id',flat=True)).filter(is_active=True)
            except ObjectDoesNotExist:	
                return json.Response("Comission not found",404, False)

        if group_code !='new':
            try:
                obj = Commission.objects.get(group_code=group_code,is_deleted=False).id
                mapped_commission=BranchMstr.objects.filter(id__in=CommissionMapping.objects.filter(commission_id=obj).values_list('branch_id',flat=True),is_active=True)
                commission=BranchMstr.objects.exclude(id__in=CommissionMapping.objects.values_list('branch_id',flat=True)).filter(is_active=True)
                commission = mapped_commission.union(commission)

            except ObjectDoesNotExist:	
                return json.Response("Comission not found",404, False)

        if request.method == 'GET':
            serializer = BranchSzr(commission,many=True)   
            if serializer:
                return json.Response(serializer.data,200, True)
		
class PaymentView(viewsets.ViewSet):	
    @has_admin_permission	
    def create_payment(self, request):	
        import json as j	
    
        datas = j.loads(request.body.decode('utf-8'))	
        payment_code = datas['payment_code']	
        test_mode = datas['test_mode']	
    	
        payment = PaymentMstr.objects.filter(payment_code=payment_code).count()	
        if payment == 0:	
            paymenttbl = PaymentMstr(payment_code=payment_code, 	
            test_mode=test_mode)	
            paymenttbl.save()	
    
        else:	
            return json.Response("Payment code already exist",200, False)	
    
        return json.Response("Payment created Successfully",201, True)	
    
    @has_admin_permission	
    def get_payments(self, request):	
        try:		
            payment = PaymentMstr.objects.all()	
        except PaymentMstr.DoesNotExist:	
            return json.Response("No payment exist",404, False)	
    
        if request.method == 'GET':	
            serializer = PaymentSerializer(payment, many=True)	
            if serializer:	
                return json.Response(serializer.data,200, True)	
    
    @has_admin_permission	
    def get_payment(self, request,payment_code):	
        try:	
            payment = PaymentMstr.objects.get(payment_code=payment_code)	
        except PaymentMstr.DoesNotExist:	
            return json.Response("No payment exist",404, False)	
    
        if request.method == 'GET':	
            serializer = PaymentSerializer(payment)	
            if serializer:	
                return json.Response(serializer.data,200, True)


@csrf_exempt
def ForgetPassword(request):
    import json as j
    if request.method == 'POST':
        
        data = request.POST
        email = data['email']
        if 'email' not in data:
            return json.Response('Email Address is Required',404, False)
        try:
            user = Profile.objects.get(email=email,is_active=True)
            token = get_tokens_for_user(user)
            time=datetime.now()+timedelta(hours=2)
            serializer = ResetTokenSerializer(
                data={'user': user.id, 'jwt_token': token['access'],'expire_ts': time})
            if serializer.is_valid():
                serializer.save()

            context = {
                'email': email,
                'reset_password_url': "http://13.233.62.76:4200/reset-password/" + token['access'],
            }

            subject = "Reset Password"
            recepiants = email

            sendCustomMail(context, recepiants, subject,'admin_forgot.html')
            return json.Response('Email_Sent',200, True)
        except:
            return json.Response('No_User_Found',200, True)


@csrf_exempt
def save_reset_password(request):
    import json as j
    if request.method == 'POST':
        data = request.POST
        password = data['password']
        jwt_token = data['jwt_token']
        try:
            valid = AuthTokenMstr.objects.get(jwt_token=jwt_token)
        except AuthTokenMstr.DoesNotExist:
            return json.Response('Invalid Token',401, True)

        
        utc = pytz.UTC

        curnt_time = datetime.now()
        dt_string = str(valid.expire_ts)
        new_dt = dt_string[:19]
        curnt_time = datetime.strptime(str(curnt_time), '%Y-%m-%d %H:%M:%S.%f')
        expire_ts = datetime.strptime(new_dt, '%Y-%m-%d %H:%M:%S')

        curnt_time = curnt_time.replace(tzinfo=utc)
        expire_ts = expire_ts.replace(tzinfo=utc)

        if expire_ts <= curnt_time:
            return json.Response('Token is Expired',401, False)
        if 'password' not in data:
            return json.Response('New Password is Required',404, False)
        if 'jwt_token' not in data: 
            return json.Response('Token is Required',404, False)
        if jwt_token and password:
            profile_id = valid.user.id
            user = Profile.objects.get(id=profile_id)
            if user:
                newpassword = make_password(password)
                user.password = newpassword
                user.save()
                return json.Response('Password Changed Successfully',200, True)
            else:
                return json.Response('User_Not_Exists',404, False)
        else:
            return json.Response("Invalid Inputs",400, False)

class ResetPasswordView(viewsets.ViewSet):
    def send_resetpassword_admin(self,request,id):
        import json as j
        if request.method == 'GET':
            
            try:
                user = Profile.objects.get(id=id,is_active=True)
                token = get_tokens_for_user(user)
                time=datetime.now()+timedelta(hours=2)
                serializer = ResetTokenSerializer(
                    data={'user': user.id, 'jwt_token': token['access'],'expire_ts': time})
                if serializer.is_valid():
                    serializer.save()

                context = {
                    'email': user.email,
                    'reset_password_url': "http://13.233.62.76:4200/reset-password/" + token['access'],
                }

                subject = "Reset Password"
                recepiants = user.email

                sendCustomMail(context, recepiants, subject,'admin_forgot.html')
                return json.Response('Email_Sent',200, True)
            except:
                return json.Response('No_User_Found',404, False)


class SellerStatus(viewsets.ViewSet):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SellerStatus, self).dispatch(request, *args, **kwargs)

    @has_permission
    def put(self, request):
        import json as j
        datas = j.loads(request.body.decode('utf-8'))
        if 'order_id' in datas:
            order_id = datas['order_id']
        else:
            return json.Response("'order_id' key not exist",404, False)

        if 'seller_status' in datas:
            seller_status = datas['seller_status']
            order = Order.objects.get(order_id=order_id)
            status = Order.objects.filter(order_id =order_id).update(seller_status=seller_status)

        else:
            return json.Response("'seller_status' key not exist",404, False)

        return json.Response("Status Updated Successfully", 200, True)

class OrderView(viewsets.ViewSet):
    @has_admin_permission
    def list_orders(self, request, *args, **kwargs):
        try:
            current_user = Order.objects.all().order_by('-order_date')
        except Order.DoesNotExist:
            return Response({
                'status': "Error",
                'message': 'Nothing to show',
                'responseCode': status.HTTP_404_NOT_FOUND
            })

        if request.method == "GET":
            serializer = OrderSerializer(current_user,many=True).data
            for data in serializer:
                orderreport = OrderReport.objects.filter(order_id = data['order_id']).count()
                if orderreport > 0:
                    orderreport = OrderReport.objects.get(order_id = data['order_id']).feedback
                    data['report_feedback'] = orderreport
                else:
                    data['report_feedback'] = None

            return Response({
                'status': "OK",
                'message': 'Content is listed',
                'data': serializer,
                'responseCode': status.HTTP_200_OK
            })

    @has_admin_permission
    def order_details(self, request, *args, **kwargs):
        import json as j
        datas = j.loads(request.body.decode('utf-8'))
        order_id = datas['order_id']
        try:
            current_user = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({
                'status': "Error",
                'message': 'Nothing to show',
                'responseCode': status.HTTP_404_NOT_FOUND
            })

        if request.method == "POST":
            serializer = OrderSerializer_details(current_user)
        
            return Response({
                'status': "OK",
                'message': 'Content is listed',
                'data': serializer.data,
                'responseCode': status.HTTP_200_OK
            })
            
    @has_admin_permission
    def update_order_status(self, request):
        import json as j
        datas = j.loads(request.body.decode('utf-8'))
        order_id = datas['order_id']
        order_status = datas['order_status']
        reason = datas['reason']
        
        usertbl = Order.objects.get(order_id=order_id)
        if order_status == 'refund issued':
            update_order_status = Order.objects.filter(order_id=order_id).update(order_status=order_status,reason=reason)
            description = f'This order {order_id} moved to refund issue status'
        
        if order_status == 'incomplete':
            update_order_status = Order.objects.filter(order_id=order_id).update(order_status=order_status,reason=reason)
            description = f'This order {order_id} moved to incomplete status'
        
        
        store_id = usertbl.store_id
        branch_name = BranchMstr.objects.get(id = store_id).branch_name
        store_address = BranchMstr.objects.get(id = store_id).branch_address
        customer_id = usertbl.customer_id
        customer_name = Profile.objects.get(id = customer_id).first_name
        cust_phone_no = Profile.objects.get(id = customer_id).phone_number
        notification = Notification(
                order_id = order_id,
                store_id = store_id,
                customer_id = customer_id,
                title = 'order status updated',
                description = description,
                store_name = branch_name,
                address = store_address,
                customer_name = customer_name,
                phone_no = cust_phone_no,
                order_status = order_status

            )
        notification.save()
        update_order_status = Order.objects.filter(order_id=order_id).update(order_status=order_status, reason=reason)
        return json.Response("Order Status updated successfully",200, True)

class ReportView(viewsets.ViewSet):
    @has_admin_permission
    def get_report_filter(self, request, *args, **kwargs):
        
        import json as j
        if request.method == 'POST':
            data = j.loads(request.body.decode('utf-8'))
            if 'days' not in data:
                date_1 = datetime.strptime(data['to_date'], '%Y-%m-%d')
                data['to_date'] = date_1 + timedelta(days=1)
                
                order = Order.objects.filter(order_date__gte=data['from_date'],
                                                order_date__lte=data['to_date']).order_by('-order_date')
                branch=BranchMstr.objects.all()
                branch=ProfitSerializer(branch,many=True)
                var = []
                arr1 = []
                arr2 = []
                new = []
                if Order.objects.filter(order_date__gte=data['from_date'],order_date__lte=data['to_date']):
                    invoice_order = Order.objects.filter(order_date__gte=data['from_date'],order_date__lte=data['to_date']).order_by('-order_date')
                else:
                    invoice_order = Order.objects.all()
                if 'shop_name' in data:
                    invoice_order = Order.objects.filter(shop_name = data['shop_name'],order_date__gte=data['from_date'],order_date__lte=data['to_date']).order_by('-order_date')
                invoice_order = OrderSerializer(invoice_order,many = True)
                for invoice in invoice_order.data:
                    
                    values = {
                        'order_id':invoice['order_id'],
                        'order_date':invoice['order_date'],
                        'shop_name':invoice['shop_name'],
                        'payment_type':invoice['payment_type'],
                        'payment_status':invoice['payment_status'],
                        'order_price':invoice['amount'],
                        'seller_status':invoice['seller_status']
                    }
                    new.append(values)
                for item in branch.data:
        
                    orders = Order.objects.filter(order_date__gte=data['from_date'],order_date__lte=data['to_date'],store_id=item['id']).values_list('amount', flat=True)
                    commission_id = CommissionMapping.objects.filter(branch_id=item['id']).values_list('commission_id', flat=True)
                    if len(commission_id)> 0:
                        commission_id=commission_id[0]
                        percentage=Commission.objects.filter(id=commission_id).values_list('percentage', flat=True)
                        if len(percentage) > 0:
                            percentage = percentage[0]
                        else:
                            percentage=0
                    else:
                        percentage = 0
                    com_amount=round(sum(orders))*(percentage/100)
                    value = {
                        'id':item['id'],
                        'baranchname':item['branch_name'],
                        'branchcode':item['branch_code'],
                        'branchaddress':item['branch_address'],
                        'branchphone':item['branch_phone'],
                        'branchemail':item['branch_email'],
                        'total_revenue':sum(orders),
                        'total_commission':com_amount,
                    }
                    var.append(value)
                    arr2.append(float(com_amount))
                orders = Order.objects.filter(order_date__gte=data['from_date'],order_date__lte=data['to_date']).values_list('amount', flat=True)
                arr1.append(sum(orders))

            else:
                days = datetime.today() - timedelta(days=data['days'])
                
                order = Order.objects.filter(order_date__gte=days).order_by('-order_date')
                branch=BranchMstr.objects.all()
                branch=ProfitSerializer(branch,many=True)
                var = []
                arr1 = []
                arr2 = []
                new = []
                if Order.objects.filter(order_date__gte=days):
                    invoice_order = Order.objects.filter(order_date__gte=days).order_by('-order_date')
                else:
                    invoice_order = Order.objects.all()
                if 'shop_name' in data:
                    invoice_order = Order.objects.filter(shop_name = data['shop_name'],order_date__gte=days).order_by('-order_date')
                invoice_order = OrderSerializer(invoice_order,many = True)
                for invoice in invoice_order.data:
                    
                    values = {
                        'order_id':invoice['order_id'],
                        'order_date':invoice['order_date'],
                        'shop_name':invoice['shop_name'],
                        'payment_type':invoice['payment_type'],
                        'payment_status':invoice['payment_status'],
                        'order_price':invoice['amount'],
                        'seller_status':invoice['seller_status']

                    }
                    new.append(values)
                
                for item in branch.data:
        
                    orders = Order.objects.filter(order_date__gte=days,store_id=item['id']).values_list('amount', flat=True)
                    commission_id = CommissionMapping.objects.filter(branch_id=item['id']).values_list('commission_id', flat=True)
                    if len(commission_id)> 0:
                        commission_id=commission_id[0]
                        percentage=Commission.objects.filter(id=commission_id).values_list('percentage', flat=True)
                        if len(percentage) > 0:
                            percentage = percentage[0]
                        else:
                            percentage=0
                    else:
                        percentage = 0
                    com_amount=round(sum(orders))*(percentage/100)
                    value = {
                        'id':item['id'],
                        'baranchname':item['branch_name'],
                        'branchcode':item['branch_code'],
                        'branchaddress':item['branch_address'],
                        'branchphone':item['branch_phone'],
                        'branchemail':item['branch_email'],
                        'total_revenue':sum(orders),
                        'total_commission':com_amount,
                    }
                    var.append(value)
                    arr2.append(float(com_amount))
                orders = Order.objects.filter(order_date__gte=days).values_list('amount', flat=True)
                arr1.append(sum(orders))
                    
            order_serializer = Orderserializers(order, many=True)
            return Response({
                'status': "OK",
                'message': 'Content is listed',
                "order": order_serializer.data,
                "profit": var,
                "total_revenue":sum(arr1),
                "total_profit":sum(arr2),
                "invoice_report":new,
                'responseCode': status.HTTP_200_OK
            })

        
