from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.dashboard, name="dashboard"),
    path('', views.home, name="home"),
    path('fetch_patient_data_details/', views.fetch_patient_data_details, name='fetch_patient__details'),
    path('add-departments/', views.departments, name="departments"),
    path('update-departments/<int:department_id>', views.departments_update, name="departments_update"),
    # path('delete-departments/<int:department_id>', views.departments_delete, name="departments_delete"),
    path('add-doctors/', views.doctors, name="doctors"),
    path('update-doctors/<int:doctor_id>', views.doctors_update, name="doctors_update"),
    # path('delete-doctors/<int:doctor_id>', views.doctors_delete, name="doctors_delete"),
    path('add-users/', views.dataentryoperator, name="users"),
    path('update-users/<int:pk>', views.dataentryoperator_update, name="dataentryoperator_update"),
    # path('delete-users/<int:pk>', views.dataentryoperator_delete, name="dataentryoperator_delete"),
    path('accounts/login/',views.signin,name='signin'),
    path('accounts/logout/',views.signout,name='signout'),
    path('add-patients/',views.add_patient,name='add_patient'),
    path('show-patients/', views.show_patients, name="show_patients"),
    path('show-patients-data/', views.show_patients_data, name="show_patients_data"),
    path('report-patients/', views.show_patients_report, name="show_patients_report"),
    path('report-patients-user/', views.show_patients_report_userwise, name="show_patients_report_userwise"),
    path('report-patients-location/', views.location_wise_report, name="location_wise_report"),
    path('get-doctors-by-department/',views.get_doctors_by_department,name='get_doctors_by_department'),
    # path('delete-patients/<int:pk>', views.delete_patients, name="delete_patients"),
    path('update-patients/<int:pk>', views.update_patients, name="update_patients"),

    path('show-department-report/', views.department_wise_report, name="department_wise_report"),
    path('show-patients-ipd-data/', views.show_patients_data_ipd, name="show_patients_data_ipd"),

    path('show-patient-ipd/', views.show_patients_ipd, name="show_patients_ipd")
    # path('opd-patients/', views.OPDPatientListCreateView.as_view(), name='opd-patient-list-create'),
]