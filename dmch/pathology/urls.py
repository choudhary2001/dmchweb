
# In urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('fetch_patient_data/', views.fetch_patient_data, name='fetch_patient_data'),
    path('fetch_patient_data_details/', views.fetch_patient_data_details, name='fetch_patient_data_details'),

    path('add-doctors/', views.doctors, name="pathology_doctors"),
    path('update-doctors/<int:doctor_id>', views.doctors_update, name="pathology_doctors_update"),
    path('delete-doctors/<int:doctor_id>', views.doctors_delete, name="pathology_doctors_delete"),

    path('add-departments/', views.departments, name="pathology_departments"),
    path('update-departments/<int:department_id>', views.departments_update, name="pathology_departments_update"),
    path('delete-departments/<int:department_id>', views.departments_delete, name="pathology_departments_delete"),

    path('create_testcode/', views.create_testcode, name='create_testcode'),
    path('test-code/<int:pk>/update/', views.update_testcode, name='update_testcode'),
    path('test-code/<int:pk>/delete/', views.delete_testcode, name='delete_testcode'),

    # URL patterns for patient_registration model
    path('create_patient_registration/', views.create_patient_registration, name='create_patient_registration'),
    path('patient_patient_registration/', views.patient_registration_view, name='patient_registration_view'),
    path('patient_registration_view_print/', views.patient_registration_view_print, name='patient_registration_view_print'),
    path('update_patient_registration/<int:pk>/', views.update_patient_registration, name='update_patient_registration'),
    path('delete_patient_registration/<int:pk>/', views.delete_patient_registration, name='delete_patient_registration'),

    # URL patterns for test_report model
    path('create_test_report/', views.create_test_report, name='create_test_report'),
    # path('create_test_report_view/', views.create_test_report_view, name='create_test_report_view_print'),
    path('create_test_report_view_print/', views.create_test_report_view, name='create_test_report_view'),
    path('create_test_report_view_print/', views.create_test_report_view_print, name='create_test_report_view_print'),
    path('update_test_report/<int:pk>/', views.update_test_report, name='update_test_report'),
    path('delete_test_report/<int:pk>/', views.delete_test_report, name='delete_test_report'),

    # URL patterns for stool_test model
    path('create_stool_test/', views.create_stool_test, name='create_stool_test'),
    # path('create_stool_test_print/', views.create_stool_test, name='create_stool_test_print'),
    path('stool_test_report_view/', views.stool_test_report_view, name='stool_test_report_view'),
    path('stool_test_report_view_print/', views.stool_test_report_view_print, name='stool_test_report_view_print'),
    path('update_stool_test/<int:pk>/', views.update_stool_test, name='update_stool_test'),
    path('delete_stool_test/<int:pk>/', views.delete_stool_test, name='delete_stool_test'),

    # URL patterns for ctest_report model
    path('create_ctest_report/', views.create_ctest_report, name='create_ctest_report'),
    # path('create_ctest_report_print/', views.create_ctest_report, name='create_ctest_report_print'),
    path('c_test_report_view/', views.c_test_report_view, name='c_test_report_view'),
    path('c_test_report_view_print/', views.c_test_report_view_print, name='c_test_report_view_print'),
    path('update_ctest_report/<int:pk>/', views.update_ctest_report, name='update_ctest_report'),
    path('delete_ctest_report/<int:pk>/', views.delete_ctest_report, name='delete_ctest_report'),

    # URL patterns for cbc_test model
    path('create_cbc_test/', views.create_cbc_test, name='create_cbc_test'),
    # path('create_cbc_test_print/', views.create_cbc_test_print, name='create_cbc_test_print'),
    path('cbc_test_report_view/', views.cbc_test_report_view, name='cbc_test_report_view'),
    path('cbc_test_report_view_print/', views.cbc_test_report_view_print, name='cbc_test_report_view_print'),
    path('update_cbc_test/<int:pk>/', views.update_cbc_test, name='update_cbc_test'),
    path('delete_cbc_test/<int:pk>/', views.delete_cbc_test, name='delete_cbc_test'),

    # URL patterns for serology_test model
    path('create_serology_test/', views.create_serology_test, name='create_serology_test'),
    # path('create_serology_test_print/', views.create_serology_test_print, name='create_serology_test_print'),
    path('serology_test_report_view/', views.serology_test_report_view, name='serology_test_report_view'),
    path('serology_test_report_view_print/', views.serology_test_report_view_print, name='serology_test_report_view_print'),
    path('update_serology_test/<int:pk>/', views.update_serology_test, name='update_serology_test'),
    path('delete_serology_test/<int:pk>/', views.delete_serology_test, name='delete_serology_test'),

    # URL patterns for urine_test model
    path('create_urine_test/', views.create_urine_test, name='create_urine_test'),
    # path('create_urine_test/', views.create_urine_test_print, name='create_urine_test_print'),
    path('urine_test_report_view/', views.urine_test_report_view, name='urine_test_report_view'),
    path('urine_test_report_view_print/', views.urine_test_report_view_print, name='urine_test_report_view_print'),
    path('update_urine_test/<int:pk>/', views.update_urine_test, name='update_urine_test'),
    path('delete_urine_test/<int:pk>/', views.delete_urine_test, name='delete_urine_test'),

]
