from .models import *
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm


class EmployeeForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=InventoryUser.ROLE)

    class Meta:
        model = EmployeeModel
        fields = ['employee_name', 'employee_contact', 'email', 'role','employee_address', 'employee_picture']
    employee_picture = forms.ImageField()

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
        fields = ['customer_name', 'customer_phone', 'customer_email','customer_dob', 'customer_address']
        
        widgets = {
            'customer_dob': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date'}),
        }
        
class MedicineCategoryForm(forms.ModelForm):
    class Meta:
        model = MedicineCategoryModel
        fields = "__all__"
        
class MedicineUnitForm(forms.ModelForm):
    class Meta:
        model = MedicineUnitModel
        fields = "__all__"
        
class MedicineForm(forms.ModelForm):
    class Meta:
        model = MedicineModel
        fields = [
            'medicine_name', 'medicine_type', 'pack_units', 'pack_size',
            'unit_price', 'medicine_category', 'medicine_picture', 'description'
        ]

    def __init__(self, *args, **kwargs):
        super(MedicineForm, self).__init__(*args, **kwargs)
        self.fields['medicine_category'].widget.attrs.update({'class': 'select2'})
    
    
class MedicineStockForm(forms.ModelForm):
    class Meta:
        model = MedicineStockModel
        fields = '__all__'
        exclude = ['created_by', 'total_amount']
        
    def __init__(self, *args, **kwargs):
        super(MedicineStockForm, self).__init__(*args, **kwargs)
        self.fields['medicine'].widget.attrs.update({'class': 'select2'})
        

class BottleBreakageForm(forms.ModelForm):
    class Meta:
        model = BottleBreakageModel
        fields = ['medicine', 'lost_quantity', 'date_time', 'reason', 'responsible_employee']
        
        widgets = {
            'date_time': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date'}),
        }


class BillingForm(forms.ModelForm):
    class Meta:
        model = BillingModel
        fields = ['customer_user', 'tax', 'discount', 'billing_status']

    def __init__(self, *args, **kwargs):
        super(BillingForm, self).__init__(*args, **kwargs)
        self.fields['customer_user'].widget.attrs.update({'class': 'select2'})

class BillingItemForm(forms.ModelForm):
    medicine = forms.ModelChoiceField(queryset=MedicineModel.objects.all())

    class Meta:
        model = BillingItemModel
        fields = ['medicine', 'medicine_quantity']

        
class SignInForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
