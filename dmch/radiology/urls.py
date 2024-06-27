# urls.py

from django.urls import path
from . import views

urlpatterns = [

    path('add-departments/', views.departments, name="radiology_departments"),
    path('update-departments/<int:department_id>', views.departments_update, name="radiology_departments_update"),
    # path('delete-departments/<int:department_id>', views.departments_delete, name="radiology_departments_delete"),

    path('add-doctors/', views.doctors, name="radiology_doctors"),
    path('update-doctors/<int:doctor_id>', views.doctors_update, name="radiology_doctors_update"),
    # path('delete-doctors/<int:doctor_id>', views.doctors_delete, name="radiology_doctors_delete"),

    path('get-doctors-by-department/',views.get_doctors_by_department,name='radiology_get_doctors_by_department'),
    path('get-investigation-by-department/',views.get_investigation_by_department,name='get_investigation_by_department'),

    path('add-investigations/', views.investigations, name="radiology_investigations"),
    path('update-investigations/<int:investigation_id>', views.investigationss_update, name="radiology_investigations_update"),
    path('delete-investigations/<int:investigation_id>', views.investigations_delete, name="radiology_investigations_delete"),

    path('add-sub-unit/', views.radiology_sub_unit, name="radiology_sub_unit"),
    path('update-sub-unit/<int:sub_unit_iid>', views.radiology_sub_unit_update, name="radiology_sub_unit_update"),
    path('delete-sub-unit/<int:sub_unit_iid>', views.radiology_sub_unit_delete, name="radiology_sub_unit_delete"),


    path('add-report/', views.add_radiology_report, name="add_radiology_report"),
    path('show-report/', views.show_radiology_report, name="show_radiology_report"),
    path('show-report-print/', views.print_radiology_report, name="print_radiology_report"),
    path('edit-report/<int:radiology_id>/', views.update_radiology_report, name="update_radiology_report"),
    path('delete-report/<int:radiology_id>/', views.delete_radiology_report, name="delete_radiology_report"),

]
