# urls.py

from django.urls import path
from . import views

urlpatterns = [

    # path('add-departments/', views.departments, name="drug_departments"),
    # path('update-departments/<int:department_id>', views.departments_update, name="drug_departments_update"),
    # path('delete-departments/<int:department_id>', views.departments_delete, name="drug_departments_delete"),
    path('get_medicine_names_by_type/', views.get_medicine_names_by_type, name='get_medicine_names_by_type'),
    path('stock/add/', views.stock_add_view, name='medicine_stock_add_view'),
    path('received/stock/view/', views.receivedsupply_details_view, name='medicine_receivedsupply_details_view'),
    path('received/stock/print/', views.receivedsupply_details_print, name='medicine_receivedsupply_details_print'),
    path('supply/view/print/', views.supply_details_view_print, name='medicine_supply_details_view_print'),
    path('supply/view/', views.supply_details_view, name='medicine_supply_details_view'),
    path('supply/medicine/', views.medicine_supply_add_view, name='medicine_supply_add_view'),
    path('supply/medicine/<str:consumption_id>/update/', views.medicine_supply_update_view, name='medicine_supply_update_view'),
    path('supply/medicine/<str:consumption_id>/delete/', views.medicine_supply_delete_view, name='medicine_supply_delete_view'),
    path('get/medicine/', views.get_medicine_details, name='get_medicine_details'),
    path('user/medicine/', views.supply_details_user_view, name='supply_details_user_view'),
    path('user/medicine/print/', views.supply_details_user_view_print, name='supply_details_user_view_print'),
    path('supply/<int:supply_id>/update/', views.supply_update_view, name='medicine-supply-update'),
    path('supply/<int:supply_id>/delete/', views.supply_delete_view, name='medicine_supply-delete'),
    path('itemwise/consumption/', views.get_consumption_and_remaining_quantity, name='get_consumption_and_remaining_quantity'),


]
