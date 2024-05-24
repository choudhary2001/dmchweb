from django.contrib import admin

from .models import *

admin.site.register(PathologyDepartment)
admin.site.register(PathologyDoctor)
admin.site.register(Testcode)
admin.site.register(Patient_registration)
admin.site.register(Test_report)
admin.site.register(Urine_test)
admin.site.register(Stool_test)
admin.site.register(Ctest_report)
admin.site.register(Cbc_test)
admin.site.register(Serology_test)