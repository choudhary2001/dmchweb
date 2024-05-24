from django.urls import path
from . import views

urlpatterns = [

    path('issue-blood/', views.issue_blood_add, name="issue_blood_add"),
    path('issue-blood-data/', views.issue_blood_view, name="issue_blood_view"),

    path('donate-blood/', views.donate_blood_add, name="donate_blood_add"),
    path('donate-blood-data/', views.donate_blood_view, name="donate_blood_view"),

    path('blood-fetch-data/', views.blood_fetch_data, name="blood_fetch_data"),
    path('blood-stock-data/', views.blood_stocks, name="blood_stocks"),

]