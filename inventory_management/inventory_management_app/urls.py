from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('',views.user_login,name='user_login'),
    path('user_logout/',user_logout,name='user_logout'),
    path('dashboard/',dashboard,name='dashboard'),
    path('employee-list/',employee_list,name='employee_list'),
    path('add-employee/',add_employee,name='add_employee'),
    path('update-employee/<str:pk>/',update_employee,name='update_employee'),
    path('delete-employee/<str:pk>/',delete_employee,name='delete_employee'),
    
    # --------------Customer Route
    path('customer-list/',customer_list,name='customer_list'),
    path('add-customer/',add_customer,name='add_customer'),
    path('update-customer/<str:customer_id>/',update_customer,name='update_customer'),
    path('delete-customer/<str:customer_id>/',delete_customer,name='delete_customer'),
    # --------------Medicine Category Route
    path('medicine_category-list/',medicine_category_list,name='medicine_category_list'),
    path('add-medicine_category/',add_medicine_category,name='add_medicine_category'),
    path('update-medicine_category/<str:pk>/',update_medicine_category,name='update_medicine_category'),
    path('delete-medicine_category/<str:pk>/',delete_medicine_category,name='delete_medicine_category'),
    
     # --------------Medicine Route
    path('add-medicine/', add_medicine, name='add_medicine'),
    path('update-medicine/<int:pk>/', update_medicine, name='update_medicine'),
    path('delete-medicine/<int:pk>/', delete_medicine, name='delete_medicine'),
    path('list-medicine/', medicine_list, name='medicine_list'),
    
     # --------------Medicine Stock Route
     path('medicine-stock-list/', medicine_stock_list, name='medicine_stock_list'),
     path('add-medicine-stock/', add_medicine_stock, name='add_medicine_stock'),
     path('update-medicine-stock/<int:pk>', update_medicine_stock, name='update_medicine_stock'),
     path('delete-medicine-stock/<int:pk>', delete_medicine_stock, name='delete_medicine_stock'),
     path('low-stocks/', low_stocks, name='low_stocks'),
     # --------------Bottle Breakage Route
     path('bottle-breakage-list/', bottle_breakage_list, name='bottle_breakage_list'),
     path('add-bottle-breakage/', add_bottle_breakage, name='add_bottle_breakage'),
     path('update-bottle-breakage/<int:pk>', update_bottle_breakage, name='update_bottle_breakage'),
     path('delete-bottle-breakage/<int:pk>', delete_bottle_breakage, name='delete_bottle_breakage'),
     
     #--------Order Route
     path('order-list/', order_list, name='order_list'),
     path('add-order/', order_create, name='order_create'),
     path('update-order/<int:pk>', order_update, name='order_update'),
     path('delete-order/<int:pk>', order_delete, name='order_delete'),
     #-------Invoice
     path('invoice-list', invoice_list, name='invoice_list'),
     path('invoice/<str:order_id>', invoice, name='invoice'),
     path('inventory-report/', inventory_report, name='inventory_report'),
     path('wastage-report/', wastage_report, name='wastage_report'),    
     path('billing-trends-report/', billing_trends_report, name='billing_trends_report'),    
     
]