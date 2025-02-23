from django.urls import path
from .views import *

urlpatterns = [
    path('',index,name='index'),
    path('employee-list/',employee_list,name='employee_list'),
    path('add-employee/',add_employee,name='add_employee'),
    path('update-employee/<str:pk>/',update_employee,name='update_employee'),
    path('delete-employee/<str:pk>/',delete_employee,name='delete_employee'),
]