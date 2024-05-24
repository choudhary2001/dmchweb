from django.contrib import admin
import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from .models import *

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_role', 'main_department', 'created_at')
    list_filter = ('user', 'user_role', 'main_department', 'created_at')
    search_fields = ('user', 'user_role', 'main_department', 'created_at')


admin.site.register(Profile, ProfileAdmin)

admin.site.register(Department)
admin.site.register(Doctor)

# Customize the site header
admin.site.site_header = 'DMCH DARBHANGA'


# Define a custom admin action to export selected objects to Excel
def export_to_excel(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="exported_data.csv"'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(field.verbose_name) for field in queryset.model._meta.fields
    ])
    for obj in queryset:
        writer.writerow([smart_str(getattr(obj, field.name)) for field in queryset.model._meta.fields])
    return response

export_to_excel.short_description = "Export to Excel"

class PatientAdmin(admin.ModelAdmin):
    list_display = ('regid', 'user', 'name', 'gender', 'year', 'month', 'days', 'mobno', 'address', 'district', 'policest', 'pincode', 'department', 'doctor', 'visittype', 'revisit', 'revisitid', 'redcardid', 'redcardtype', 'appointment_date', 'custom_visit_charge', 'de')  
    list_filter = ('name', 'user', 'gender', 'mobno', 'address', 'district', 'policest', 'pincode', 'de', 'revisit', 'visittype', 'appointment_date')  
    search_fields = ('name','regid')  
    actions = [export_to_excel]  

    def custom_visit_charge(self, obj):
        if obj.de is not None:
            return 'Rs 0 /-'
        elif obj.visittype == 'Unknown':
            return 'Rs 0 /-'
        elif obj.redcard:
            return 'Rs 0 /-'
        elif obj.revisit == 'Revisit':
            return 'Rs 0 /-'
        else:
            return 'Rs 5 /-'

    custom_visit_charge.short_description = 'Visit Charge' 

# Register the Supply model with the custom admin class
admin.site.register(Patient, PatientAdmin)
