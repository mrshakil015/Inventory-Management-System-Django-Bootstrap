from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('',views.user_login,name='user_login'),
    path('user-logout/',user_logout,name='user_logout'),
    path('change-password/',change_password,name='change_password'),
    path('dashboard/',views.dashboard,name='dashboard'),
    
    path("upload-medicine/", upload_medicine, name="upload_medicine"),
    
    #---------Employee Route
    path('employee-list/',employee_list,name='employee_list'),
    path('add-employee/',add_employee,name='add_employee'),
    path('update-employee/<str:pk>/',update_employee,name='update_employee'),
    path('delete-employee/<str:pk>/',delete_employee,name='delete_employee'),
    path('delete-selected-employee',delete_selected_employee,name="delete_selected_employee"),
    
    # --------------Customer Route
    path('customer-list/',customer_list,name='customer_list'),
    path('add-customer/',add_customer,name='add_customer'),
    path('update-customer/<str:customer_id>/',update_customer,name='update_customer'),
    path('delete-customer/<str:customer_id>/',delete_customer,name='delete_customer'),
    path('delete-selected-customer',delete_selected_customers, name="delete_selected_customers"),
    # --------------Medicine Category Route
    path('medicine_category-list/',medicine_category_list,name='medicine_category_list'),
    path('add-medicine_category/',add_medicine_category,name='add_medicine_category'),
    path('update-medicine_category/<str:pk>/',update_medicine_category,name='update_medicine_category'),
    path('delete-medicine_category/<str:pk>/',delete_medicine_category,name='delete_medicine_category'),
    path('delete-selected-medicine-categories',delete_selected_medicine_categories,name="delete_selected_medicine_categories"),
    
    # --------------Medicine Unit Route
    path('medicine_unit-list/',medicine_unit_list,name='medicine_unit_list'),
    path('delete-selected-medicine-units/', delete_selected_medicine_units, name='delete_selected_medicine_units'),
    path('add-medicine_unit/',add_medicine_unit,name='add_medicine_unit'),
    path('update-medicine_unit/<str:pk>/',update_medicine_unit,name='update_medicine_unit'),
    path('delete-medicine_unit/<str:pk>/',delete_medicine_unit,name='delete_medicine_unit'),
    
     # --------------Medicine Route
    path('add-medicine/', add_medicine, name='add_medicine'),
    path('update-medicine/<int:pk>/', update_medicine, name='update_medicine'),
    path('delete-medicine/<int:pk>/', delete_medicine, name='delete_medicine'),
    path('delete-selected-medicines/', delete_selected_medicines, name='delete_selected_medicines'),
    path('list-medicine/', medicine_list, name='medicine_list'),
    path('medicine/<int:pk>/', medicine_detail, name='medicine_detail'),
    
     # --------------Medicine Stock Route
     path('medicine-stock-list/', medicine_stock_list, name='medicine_stock_list'),
     path('add-medicine-stock/', add_medicine_stock, name='add_medicine_stock'),
     path('update-medicine-stock/<int:pk>', update_medicine_stock, name='update_medicine_stock'),
     path('delete-medicine-stock/<int:pk>', delete_medicine_stock, name='delete_medicine_stock'),
     path('delete-selected-stocks',delete_selected_stocks,name="delete_selected_stocks"),
     path('low-stocks/', low_stocks, name='low_stocks'),
     path('upload-stock/', upload_medicine_stock, name='upload_medicine_stock'),
     # --------------Bottle Breakage Route
     path('bottle-breakage-list/', bottle_breakage_list, name='bottle_breakage_list'),
     path('add-bottle-breakage/', add_bottle_breakage, name='add_bottle_breakage'),
     path('update-bottle-breakage/<int:pk>', update_bottle_breakage, name='update_bottle_breakage'),
     path('delete-bottle-breakage/<int:pk>', delete_bottle_breakage, name='delete_bottle_breakage'),
     path('delete-selected-bottle-breakages/', delete_selected_bottle_breakages, name='delete_selected_bottle_breakages'),
     
     #--------Billing Route
     path('billing-list/', billing_list, name='billing_list'),
     path('add-billing/', billing_create, name='billing_create'),
     path('update-billing/<int:pk>', billing_update, name='billing_update'),
     path('delete-billing/<int:pk>', billing_delete, name='billing_delete'),
     path('delete-selected-billings/', delete_selected_billings, name='delete_selected_billings'),
     #-------Invoice
     path('invoice-list', invoice_list, name='invoice_list'),
     path('invoice/<str:billing_id>', invoice, name='invoice'),
     path('send-invoice/<int:billing_id>/', send_invoice_email, name='send_invoice_email'),
     path('send-invoice-whatsapp/<int:billing_id>/', send_invoice_via_whatsapp, name='send_invoice_via_whatsapp'),
     
     #---------Report
     path('inventory-report/', inventory_report, name='inventory_report'),
     path('wastage-report/', wastage_report, name='wastage_report'),    
     path('billing-trends-report/', billing_trends_report, name='billing_trends_report'),   
     
     path('get-customer-by-phone/<str:phone>/', get_customer_by_phone, name='get-customer-by-phone'),
    path('get-customer-by-phone-autocomplete/', get_customer_by_phone_autocomplete, name='get-customer-by-phone-autocomplete'),
     
]