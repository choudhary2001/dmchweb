from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('add-departments/', views.departments, name="departments"),
    path('update-departments/<int:department_id>', views.departments_update, name="departments_update"),
    path('delete-departments/<int:department_id>', views.departments_delete, name="departments_delete"),
    path('add-doctors/', views.doctors, name="doctors"),
    path('update-doctors/<int:doctor_id>', views.doctors_update, name="doctors_update"),
    path('delete-doctors/<int:doctor_id>', views.doctors_delete, name="doctors_delete"),
    path('add-users/', views.dataentryoperator, name="users"),
    path('update-users/<int:pk>', views.dataentryoperator_update, name="dataentryoperator_update"),
    path('delete-users/<int:pk>', views.dataentryoperator_delete, name="dataentryoperator_delete"),
    path('accounts/login/',views.signin,name='signin'),
    path('accounts/logout/',views.signout,name='signout'),
    path('add-patients/',views.add_patient,name='add_patient'),
    path('show-patients/', views.show_patients, name="show_patients"),
    path('report-patients/', views.show_patients_report, name="show_patients_report"),
    path('report-patients-user/', views.show_patients_report_userwise, name="show_patients_report_userwise"),
    path('get-doctors-by-department/',views.get_doctors_by_department,name='get_doctors_by_department'),
    path('delete-patients/<int:pk>', views.delete_patients, name="delete_patients"),
    path('update-patients/<int:pk>', views.update_patients, name="update_patients"),

    # path('opd-patients/', views.OPDPatientListCreateView.as_view(), name='opd-patient-list-create'),
]