from django.contrib import admin

from .models import *

admin.site.register(RadiologyDepartment)
admin.site.register(Investigation)
admin.site.register(SubUnit)
admin.site.register(RadiologyDoctor)
admin.site.register(Radiology)
