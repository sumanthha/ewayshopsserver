from django.urls import path
from customer import views


urlpatterns = [
    
    path('signup_next', views.save_signup_next, name='save_signup_next'),
    path('signup', views.CustomerSignUpView.as_view()),
    path('forget_password/', views.ForgetPassword, name='forget_password'),
    path('reset_password/', views.save_reset_password, name='reset_password'),
    path('storelist',views.StoreListAPIView.as_view({'post':'get_store_list'})),
    path('itemlist',views.ProductListView.as_view({'post':'get_item_list'})),
    path('customer_profile',views.CustomerProfileDetails.as_view({'get':'get_customer_profile'})),
    path('customer_profile/update',views.CustomerProfileDetails.as_view({'put':'update_customer_profile'})),
    path('add_cart',views.CustomerCart.as_view({'post':'add_cart'})),
    path('update_cart',views.CustomerCart.as_view({'put':'update_cart'})),
    path('delete_cart',views.CustomerCart.as_view({'delete':'delete_cart'})),
    path('view_cart',views.CustomerCart.as_view({'get':'view_cart'})),
    path('add_wishlist',views.CustomerWishList.as_view({'post':'add_wishlist'})),
    path('remove_wishlist',views.CustomerWishList.as_view({'delete':'remove_wishlist'})),
    path('get_wishlist',views.CustomerWishList.as_view({'get':'get_wishlist'})),
    path('order_status_history/',views.OrderView.as_view({'get':'get_order_history'})),
    path('report-order/', views.OrderView.as_view({'post': 'post_report'})),
    path('order/',views.OrderView.as_view({'post':'order_details'})),
    path('get_notification',views.NotificationListAPIView.as_view({'get':'get_notification_list'})),
    path('notification_count',views.NotificationListAPIView.as_view({'get':'notification_count'})),
    path('delete_notification',views.NotificationListAPIView.as_view({'delete':'delete_notification'})),
    path('checkout',views.OrderInfo.as_view({'post':'create_order'})),
    path('single_storelist/<int:id>',views.StoreListAPIView.as_view({'get':'get_single_storelist'})),
    path('payment_option',views.OrderInfo.as_view({'put':'payment_option'})),
    path('payment_capture',views.OrderInfo.as_view({'post':'payment_capture_check'})),
    path('get_branch_item_list',views.ProductListView.as_view({'post':'get_branch_item_list'}))
    

]