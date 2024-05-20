# urls.py

from django.urls import path
from . import views

urlpatterns = [

    path('add-departments/', views.departments, name="store_departments"),
    path('update-departments/<int:department_id>', views.departments_update, name="store_departments_update"),
    path('delete-departments/<int:department_id>', views.departments_delete, name="store_departments_delete"),

    path('add-products/', views.product_add_view, name="product_add_view"),
    path('view-products/', views.product_details_view, name="product_details_view"),
    path('view-stock-products/', views.product_stock_view_print, name="product_stock_view_print"),
    path('view-products/print/', views.supply_details_view_print, name="supply_details_view_print"),
    path('update-products/<str:product_id>/', views.product_update_view, name="product_update_view"),

    path('get_product_details_view/', views.get_product_details_view, name="get_product_details_view"),

    path('add-products-consumption/', views.product_add_consumption, name="product_add_consumption"),
    path('view-products-consumption/', views.product_consumption_details_view, name="product_consumption_details_view"),
    path('view-products-consumption/print/', views.product_consumption_details_view_print, name="product_consumption_details_view_print"),
    # path('update-products-consumption/<str:product_id>/', views.product_consumption_update_view, name="product_consumption_update_view"),

]
