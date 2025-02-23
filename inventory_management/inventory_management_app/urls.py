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
]