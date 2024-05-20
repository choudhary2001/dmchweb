from django.contrib import admin

from .models import *

admin.site.register(StoreDepartment)

# class StoreProduct(admin.ModelAdmin):
#     list_display = ('product_id', 'product_name', 'sdepartment', 'company_name', 'quantity', 'stock_quantity', 'bill_no', 'bill_date', 'chalan_no', 'chalan_date', 'sp_order_no', 'sp_order_date', 'received_date', 'created_at')  
#     list_filter = ('product_id', 'product_name', 'sdepartment', 'company_name', 'quantity', 'stock_quantity', 'bill_no', 'bill_date', 'chalan_no', 'chalan_date', 'sp_order_no', 'sp_order_date', 'received_date', 'created_at')  
#     search_fields = ('product_name','company_name')  
# admin.site.register(Product, StoreProduct)
admin.site.register(Product)
admin.site.register(ProductConsumption)
