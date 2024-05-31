# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('add-bht/', views.add_bht_report, name="add_bht_report"),
    path('show-bht-report/', views.show_bht_report, name="show_bht_report"),
    path('print-bht-report/', views.print_bht_report, name="print_bht_report"),
    path('add-injuiry/', views.add_injuiry_report, name="add_injuiry_report"),
    path('show-injuiry-report/', views.show_injuiry_report, name="show_injuiry_report"),
    path('print-injuiry-report/', views.print_injuiry_report, name="print_injuiry_report"),
    path('add-death/', views.add_death_report, name="add_death_report"),
    path('show-death-report/', views.show_death_report, name="show_death_report"),
    path('print-death-report/', views.print_death_report, name="print_death_report"),

]