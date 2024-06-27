from django.contrib import admin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from .models import *

class MedicineConsumptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'departpment', 'regno', 'patient_name', 'patient', 'created_at')
    list_filter = ('user', 'departpment', 'regno', 'patient_name')
    search_fields = ( 'regno', 'patient_name')


class MedicineAdmin(admin.ModelAdmin):
    list_display = ( 'medicine_id','departpment',  'product',  'created_at')
    list_filter = ( 'medicine_id', 'departpment',  'product', ('created_at', DateRangeFilter))
    search_fields = ( 'medicine_id',)


admin.site.register(MedicineConsumption, MedicineConsumptionAdmin)
admin.site.register(Medicine, MedicineAdmin)