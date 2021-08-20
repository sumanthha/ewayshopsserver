"""maligai_sheet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users import views
from rest_framework_simplejwt.views import TokenRefreshView
from ewayshop import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    #common API
    path('login/', views.MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forget_password/', views.ForgetPassword, name='forget_password'),
    path('reset_password/', views.save_reset_password, name='reset_password'),

    # Bussiness admin API's
    path('bussiness_admin/', include('users.urls')),
    # store admin API's
    path('store/', include('store.urls')),
    # customer admin API's
    path('customer/', include('customer.urls')),
    
    # Custome API's
    path('customer_signup/', views.SignUpView.as_view()),
    path('request_branch/', views.CreateRequestBranch.as_view()),
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
