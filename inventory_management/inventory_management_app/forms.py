from .models import *
from django import forms
from django.core.exceptions import ValidationError


class EmployeeForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=InventoryUser.ROLE)

    class Meta:
        model = EmployeeModel
        fields = ['employee_name', 'employee_contact', 'email', 'role','employee_address', 'employee_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.employee_user:
            self.fields['email'].initial = self.instance.employee_user.email

    def save(self, commit=True):
        employee = super().save(commit=False)
        if employee.employee_user:
            employee.employee_user.email = self.cleaned_data['email']
            employee.employee_user.save()
        if commit:
            employee.save()
        return employee


class CustomerForm(forms.ModelForm):
    class Meta:
        model = CustomerModel
        fields = ['customer_name', 'customer_phone', 'customer_email', 'customer_address']
        
class MedicineCategoryForm(forms.ModelForm):
    class Meta:
        model = MedicineCategoryModel
        fields = "__all__"