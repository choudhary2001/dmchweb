from django.contrib import admin

from .models import *


class ProductSupplyAdmin(admin.ModelAdmin):
    list_display = ('user', 'productdetails_id', 'product_name', 'product_type', 'department', 'mfg_name', 'batch_no','stock_quantity', 'quantity', 'mfg_date', 'exp_date', 'supply_date' )
    list_filter = ('user', 'productdetails_id', 'product_name', 'product_type', 'department', )
    search_fields = ( 'productdetails_id', 'product_name', 'product_type')


class SupplyAdmin(admin.ModelAdmin):
    list_display = ('user', 'supply_id', 'indent', 'departpment', 'de','remarks', 'order_date', 'created_at'  )
    list_filter = ( 'supply_id', 'indent', 'departpment',  'de','remarks', 'order_date', 'created_at'  )
    search_fields = ('supply_id', 'indent',   'de','remarks', 'order_date', 'created_at'  )

class ProductPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'productdetails_id', 'product_name', 'product_type', 'department', 'mfg_name', 'batch_no','stock_quantity', 'quantity', 'mfg_date', 'exp_date', 'created_at' )
    list_filter = ('user', 'productdetails_id', 'product_name', 'product_type', 'department', )
    search_fields = ( 'productdetails_id', 'product_name', 'product_type')


admin.site.register(DrugDepartment)
admin.site.register(Suppliar)
admin.site.register(ProductType)
admin.site.register(ProductDetails)
admin.site.register(ProductPurchase, ProductPurchaseAdmin)
admin.site.register(ProductSupply, ProductSupplyAdmin)
admin.site.register(Order)
admin.site.register(Purchase)
admin.site.register(Supply, SupplyAdmin)
    