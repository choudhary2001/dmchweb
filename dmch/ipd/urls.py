from django.urls import path
from . import views

urlpatterns = [

    path('add-departments/', views.ipd_departments, name="ipd_departments"),
    path('update-departments/<int:department_id>', views.departments_update, name="departments_update"),
    # path('delete-departments/<int:department_id>', views.departments_delete, name="departments_delete"),
    path('add-doctors/', views.ipd_doctors, name="ipd_doctors"),
    path('update-doctors/<int:doctor_id>', views.doctors_update, name="doctors_update"),
    # path('delete-doctors/<int:doctor_id>', views.doctors_delete, name="doctors_delete"),

    path('add-patients/',views.ipd_add_patient,name='ipd_add_patient'),
    path('discharge-patient/',views.ipd_discharge_patient,name='ipd_discharge_patient'),
    # path('show-patients/', views.show_patients, name="show_patients"),
    # path('show-patients-data/', views.show_patients_data, name="show_patients_data"),
    # path('report-patients/', views.show_patients_report, name="show_patients_report"),
    # path('report-patients-user/', views.show_patients_report_userwise, name="show_patients_report_userwise"),
    path('get-doctors-by-department/',views.get_ipd_doctors_by_department,name='get_ipd_doctors_by_department'),
    # path('delete-patients/<int:pk>', views.delete_patients, name="delete_patients"),
    # path('update-patients/<int:pk>', views.update_patients, name="update_patients"),

    # path('opd-patients/', views.OPDPatientListCreateView.as_view(), name='opd-patient-list-create'),
    path('show-patients-report/', views.show_ipd_patients_report, name="show_ipd_patients_report"),

    path('show-patients/', views.fetch_ipd_patient_data, name="fetch_ipd_patient_data"),
    path('discharge-patient-data/', views.fetch_ipd_decharge_patient_data, name="fetch_ipd_decharge_patient_data"),


]