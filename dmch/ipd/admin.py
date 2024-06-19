from django.contrib import admin

from .models import *

admin.site.register(IpdDepartment)
admin.site.register(IpdDoctor)


class PatientAdmissionAdmin(admin.ModelAdmin):
    list_display = ('patient_dmission_id', 'name', 'regno', 'department', 'referby', 'appointment_date', 'discharge', 'created_at')
    search_fields = ('patient_dmission_id', 'name', 'regno', 'department__name', 'referby__name')
    list_filter = ('department', 'discharge', 'created_at')
    readonly_fields = ('patient_dmission_id', 'created_at')
    
    fieldsets = (
        (None, {
            'fields': ('patient_dmission_id', 'user', 'department', 'referby', 'patient')
        }),
        ('Patient Information', {
            'fields': ('regno', 'dr_reg_no', 'name', 'guardiannametitle', 'guardianname', 'year', 'month', 'days', 'gender', 'mobno', 'address', 'district', 'policest', 'state', 'pincode')
        }),
        ('Medical Details', {
            'fields': ('disease', 'discharge', 'death', 'lama', 'remark')
        }),
        ('Dates', {
            'fields': ('appointment_date', 'discharge_date')
        }),
        ('Additional Info', {
            'fields': ('created_at',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.patient_dmission_id:
            obj.patient_dmission_id = str(uuid.uuid4().int)[:8]
        super().save_model(request, obj, form, change)

admin.site.register(Patient_Admission, PatientAdmissionAdmin)
