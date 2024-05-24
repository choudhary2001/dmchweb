from django.contrib import admin

from .models import *

class MedicineConsumptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'departpment', 'regno', 'patient_name', 'patient', 'created_at')
    list_filter = ('user', 'departpment', 'regno', 'patient_name')
    search_fields = ('user', 'departpment', 'regno', 'patient_name')



admin.site.register(MedicineConsumption, MedicineConsumptionAdmin)
admin.site.register(Medicine)