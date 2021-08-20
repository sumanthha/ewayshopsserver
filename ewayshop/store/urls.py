from django.urls import path
from store import views


urlpatterns = [

    path('signup', views.StoreSignUpView.as_view()),
    path('profile/', views.StoreProfileDetails.as_view({'get': 'get_store_admin'})),
    path('profile/update', views.StoreProfileDetails.as_view({'put': 'update_store_admin'})),
    path('forget_password/', views.StoreForgetPassword, name='store_reset_password'),
    path('subcategory/<str:category_name>', views.StoreCategory.as_view({'get': 'get_subcategory'})),
    path('category/', views.StoreCategory.as_view({'get': 'get_category_store'})),
    path('bulk_upload/product', views.BulkUploadView.as_view({'post':'item_bulk_upload'})),
    path('product', views.InventoryView.as_view({'post':'add_product','get':'get_products'})),
    path('product/<int:id>', views.InventoryView.as_view({'get':'get_product','put':'update_product','delete':'delete_product'})),
    path('order', views.SellerOrderView.as_view({'get':'list_orders'})),
    path('order/', views.SellerOrderView.as_view({'post':'order_details'})),
    path('customer/',views.CustomerListAPIView.as_view({'get':'get_customers_list'})),
    path('order_status_update',views.SellerOrderView.as_view({'put':'update_order_status'})),
    path('discount_update/<str:item_code>',views.DiscountAPIView.as_view({'put':'discount_update'})),
    path('update_timemanagement/',views.SellerOrderView.as_view({'put':'update_timemanagement'})),
    path('order_status_count/',views.SellerOrderView.as_view({'get':'get_order_status_count'})),
    path('order_status_history/',views.SellerOrderView.as_view({'get':'get_order_history'})),
    path('order_status_count_based/',views.SellerOrderView.as_view({'get':'get_order_status_count_based'})),
    path('notification_get/',views.NotificationListAPIView.as_view({'get':'get_notification_list'})),
    path('notification_count/',views.NotificationListAPIView.as_view({'get':'get_notification_count'})),
    path('notification_delete/<int:id>',views.NotificationListAPIView.as_view({'delete':'delete_notification'})),
    path('notification_delete/',views.NotificationListAPIView.as_view({'delete':'delete_notification'})),
    path('inventory_summary/',views.InventoryView.as_view({'get':'get_inventory_summary'})),
    path('image_upload/',views.ImageAPIView.as_view({'post':'image_upload'})),
]