# urls.py

from django.urls import path
from . import views

urlpatterns = [

    path('add-report/', views.add_cardiology_report, name="add_cardiology_report"),
    path('show-report/', views.show_cardiology_report, name="show_cardiology_report"),
    path('show-report-print/', views.print_cardiology_report, name="print_cardiology_report"),
    path('delete-report/<int:cardiology_id>/', views.delete_cardiology_report, name="delete_cardiology_report"),

]
