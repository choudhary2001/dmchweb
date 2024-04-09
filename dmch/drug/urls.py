# urls.py

from django.urls import path
from . import views

urlpatterns = [

    path('add-departments/', views.departments, name="drug_departments"),
    path('update-departments/<int:department_id>', views.departments_update, name="drug_departments_update"),
    path('delete-departments/<int:department_id>', views.departments_delete, name="drug_departments_delete"),

    # Supplier URLs
    path('suppliar/add/', views.suppliar_add_view, name='suppliar-add'),
    path('suppliar/<str:suppliar_id>/update/', views.suppliar_update_view, name='suppliar-update'),
    path('suppliar/<str:suppliar_id>/delete/', views.suppliar_delete_view, name='suppliar-delete'),

    # Product Type URLs
    path('product-type/add/', views.product_type_add_view, name='product-type-add'),
    path('product-type/<str:product_type_id>/update/', views.product_type_update_view, name='product-type-update'),
    path('product-type/<str:product_type_id>/delete/', views.product_type_delete_view, name='product-type-delete'),

    path('get_product_names_by_type/', views.get_product_names_by_type, name='get_product_names_by_type'),
    path('get_product_names_by_type_purchase/', views.get_product_names_by_type_purchase, name='get_product_names_by_type_purchase'),
    path('get_product_details/', views.get_product_details, name='get_product_details'),

    # Order URLs
    path('order/add/', views.order_add_view, name='order-add'),
    path('order/view/', views.order_details_view, name='order_details_view'),
    path('order/view/print/', views.order_details_view_print, name='order_details_view_print'),
    path('order/<int:order_id>/update/', views.order_update_view, name='order-update'),
    path('order/<int:order_id>/delete/', views.order_delete_view, name='order-delete'),

    # Purchase URLs
    path('purchase/add/', views.purchase_add_view, name='purchase-add'),
    path('purchase/view/', views.purchase_details_view, name='purchase_details_view'),
    path('purchase/view/print/', views.purchase_details_view_print, name='purchase_details_view_print'),
    path('purchase/<str:purchase_id>/update/', views.purchase_update_view, name='purchase-update'),
    path('purchase/<str:purchase_id>/delete/', views.purchase_delete_view, name='purchase-delete'),

    # Supply URLs
    path('supply/add/', views.supply_add_view, name='supply-add'),
    path('supply/view/print/', views.supply_details_view_print, name='supply_details_view_print'),
    path('supply/view/', views.supply_details_view, name='supply_details_view'),
    path('supply/<str:supply_id>/update/', views.supply_update_view, name='supply-update'),
    path('supply/<str:supply_id>/delete/', views.supply_delete_view, name='supply-delete'),
]
