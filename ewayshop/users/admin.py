from django.contrib import admin
from users.models import *

# Register your models here.
@admin.register(Profile)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('email','is_admin','is_store','is_customer','is_active','pk', )

admin.site.register(UserGroup)
admin.site.register(ItemMstr)
admin.site.register(BranchItem)
admin.site.register(Order)
admin.site.register(OrderList)