from django.urls import path
from users import views


urlpatterns = [
    path('', views.UsersProfileDetails.as_view({'get': 'get_bussiness_admin'})),
    path('update/', views.UsersProfileDetails.as_view({'put': 'update_bussiness_admin'})),
    path('create_branch/', views.Branch.as_view({'post': 'create_branch_admin'})),
    path('branch/', views.Branch.as_view({'get': 'get_branches_admin'})),
    path('branch/<str:branch_code>', views.Branch.as_view({'get': 'get_branche_admin','put':'update_branch_admin','delete':'delete_branch_admin'})),
    path('create_branch_manager/', views.BranchManagerView.as_view({'post': 'create_branch_manager'})),
    path('branch_manager/', views.BranchManagerView.as_view({'get': 'get_branch_managers_admin'})),
    path('branch_manager/<str:profile_code>', views.BranchManagerView.as_view({'get': 'get_branch_manager_admin','put':'update_branch_manager_admin','delete':'delete_branch_manager_admin'})),
    path('category/', views.CategoryView.as_view({'post': 'create_category','get':'get_categories'})),
    path('category/bulk-upload', views.CategoryView.as_view({'post': 'category_bulk_upload'})),
    path('category/<str:category_code>', views.CategoryView.as_view({'get':'get_category','put':'update_category','delete':'delete_category'})),
    path('subcategory/', views.SubCategoryView.as_view({'post': 'create_subcategory','get':'get_subcategories'})),
    path('subcategory/bulk-upload', views.SubCategoryView.as_view({'post':'subcategory_bulk_upload'})),
    path('subcategory/<str:category_code>', views.SubCategoryView.as_view({'get':'get_subcategory','put':'update_subcategory','delete':'delete_subcategory'})),
    path('commission/', views.CommissionView.as_view({'post': 'create_commission','get':'get_commissions'})),
    path('commission/unmapped/<str:group_code>', views.CommissionView.as_view({'get': 'Unmapped_list'})),
    path('commission/<str:group_code>', views.CommissionView.as_view({'get':'get_commission','put':'update_commission','delete':'delete_commission','post':'commission_mapping'})),
    path('payment/', views.PaymentView.as_view({'post':'create_payment','get':'get_payments'})),
    path('payment/<str:payment_code>', views.PaymentView.as_view({'get':'get_payment'})),
    path('order', views.OrderView.as_view({'get':'list_orders'})),
    path('order/', views.OrderView.as_view({'post':'order_details'})),
    path('seller-status', views.SellerStatus.as_view({"put":"put"})),
    path('report', views.ReportView.as_view({'post':'get_report_filter'})),
    path('forget_password/<int:id>', views.ResetPasswordView.as_view({'get':'send_resetpassword_admin'})),  
    path('order_status_update/', views.OrderView.as_view({'put':'update_order_status'})),
    path('order_report', views.ReportView.as_view({'post':'get_order_report_filter'})),
    path('profit_report', views.ReportView.as_view({'post':'get_profit_report'})),
]
