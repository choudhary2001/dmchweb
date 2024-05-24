from django.contrib import admin

from .models import *

admin.site.register(BloodIssue)
admin.site.register(BloodDonate)

class BloodStockAdmin(admin.ModelAdmin):
    list_display = ('user', 'blooddonate', 'segment_no', 'bag_no', 'blood_group', 'bag_type', 'blood_type', 'status', 'add_date' )
    list_filter = ('user', 'blooddonate', 'segment_no', 'bag_no', 'blood_group', 'bag_type', 'blood_type', 'status', 'add_date' )
    search_fields = ('user', 'blooddonate', 'segment_no', 'bag_no', 'blood_group', 'bag_type', 'blood_type', 'status', 'add_date' )


admin.site.register(BloodStock, BloodStockAdmin)