from django.contrib import admin

from .models import *

admin.site.register(Patient)
admin.site.register(Profile)
admin.site.register(Department)
admin.site.register(Doctor)