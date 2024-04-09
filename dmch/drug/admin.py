from django.contrib import admin

from .models import *

admin.site.register(Supply)
admin.site.register(ProductSupply)
admin.site.register(ProductPurchase)
admin.site.register(Purchase)
