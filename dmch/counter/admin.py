from django.contrib import admin

from .models import *

admin.site.register(Patient)
admin.site.register(Profile)
admin.site.register(Department)
admin.site.register(Doctor)

# Customize the site header
admin.site.site_header = 'DMCH DARBHANGA'