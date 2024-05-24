from django.contrib import admin

from .models import *

admin.site.register(IpdDepartment)
admin.site.register(IpdDoctor)
admin.site.register(Patient_Admission)