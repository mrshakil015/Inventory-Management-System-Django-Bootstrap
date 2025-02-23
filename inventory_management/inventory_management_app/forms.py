from .models import *
from django import forms

class EmployeeForm(forms.ModelForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=InventoryUser.ROLE)
    
    class Meta:
        model = EmployeeModel
        fields = ['employee_name', 'employee_contact', 'email', 'role','employee_address', 'employee_picture']
