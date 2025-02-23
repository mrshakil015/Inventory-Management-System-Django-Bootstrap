from django.urls import path
from .views import *

urlpatterns = [
    path('',index,name='index'),
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
    
     path('add-medicine/', add_medicine, name='add_medicine'),
    path('update-medicine/<int:pk>/', update_medicine, name='update_medicine'),
    path('delete-medicine/<int:pk>/', delete_medicine, name='delete_medicine'),
    path('list-medicine/', medicine_list, name='medicine_list'),
]