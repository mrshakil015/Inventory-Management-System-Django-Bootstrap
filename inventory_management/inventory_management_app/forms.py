from .models import *
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm

class EmployeeForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=InventoryUser.ROLE)
    
    # Sidebar Access as checkboxes but stored as a string
    USER_ACCESS_CHOICES = [
        # Employee
        ('employee_management','Employee Management'),
        ('employee_view','Employee View'),
        
        ('customer_management','Customer Management'),
        ('customer_view','Customer View'),
        
        ('product_management','Product Management'),
        ('product_view','Product View'),
        
        ('low_stocks','Low Stocks'),
        ('billing_management','Billing Management'),
        ('inventory_report','Inventory Report'),
        ('wastage_report','Wastage Report'),
        ('billing_report','Billing Report'),
    ]

    user_access_list = forms.MultipleChoiceField(
        choices=USER_ACCESS_CHOICES,
        widget=forms.CheckboxSelectMultiple,  
        required=False
    )

    class Meta:
        model = EmployeeModel
        fields = ['employee_name', 'employee_contact', 'email', 'role', 'employee_address', 'employee_picture', 'user_access_list']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.employee_user:
            self.fields['email'].initial = self.instance.employee_user.email
            self.fields['role'].initial = self.instance.employee_user.role
            self.fields['user_access_list'].initial = self.instance.employee_user.get_user_access_list()

    def save(self, commit=True):
        employee = super().save(commit=False)
        if not employee.employee_user:
            return employee  # If no linked user, return without saving access list

        user = employee.employee_user
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        user.user_access_list = ','.join(self.cleaned_data['user_access_list'])  # Store as comma-separated string
        if commit:
            user.save()
            employee.save()
        return employee


class CustomerForm(forms.ModelForm):
    customer_dob = forms.CharField(
        max_length=5,
        required=False,
        help_text="Format: DD-MM",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DD-MM'}),
    )
    class Meta:
        model = CustomerModel
        fields = ['customer_name', 'customer_phone', 'customer_email','customer_dob', 'customer_address']

    def clean_customer_dob(self):
        customer_dob = self.cleaned_data.get('customer_dob')
        if customer_dob:
            try:
                day, month = map(int, customer_dob.split('-'))
                if day < 1 or day > 31 or month < 1 or month > 12:
                    raise forms.ValidationError("Invalid date. Please use the format DD-MM e.g. 21-03")
            except (ValueError, IndexError):
                raise forms.ValidationError("Invalid date format. Please use the format DD-MM e.g. 21-03")
        return customer_dob
        
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
            'medicine_name','brand_name', 'medicine_type','medicine_category', 'batch_number','pack_units', 'pack_size',
            'unit_price',  'medicine_picture', 'description'
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
        
class MedicineStockUploadForm(forms.Form):
    file = forms.FileField()
        

class BottleBreakageForm(forms.ModelForm):
    class Meta:
        model = BottleBreakageModel
        fields = ['medicine', 'lost_quantity', 'date_time', 'reason', 'responsible_employee']
        
        widgets = {
            'date_time': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super(BottleBreakageForm, self).__init__(*args, **kwargs)
        self.fields['medicine'].widget.attrs.update({'class': 'select2'})
        self.fields['responsible_employee'].widget.attrs.update({'class': 'select2'})


class BillingForm(forms.ModelForm):
    customer_phone = forms.CharField(
        max_length=15,  # Adjust the max_length as needed
        help_text="Type the number without country code. (e.g., +91)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
    )
    customer_dob = forms.CharField(
        max_length=5,
        required=False,
        help_text="Format: DD-MM",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DD-MM'}),
    )


    class Meta:
        model = BillingModel
        fields = ['customer_user', 'customer_name', 'customer_phone', 'customer_email', 'customer_dob', 'customer_address', 'discount_percentage', 'billing_status']
        
        widgets = {
            'customer_dob': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(BillingForm, self).__init__(*args, **kwargs)
        self.fields['customer_user'].widget.attrs.update({'class': 'select2'})
        self.fields['customer_user'].required = False  # Make customer_user optional

    def clean(self):
        cleaned_data = super().clean()
        customer_user = cleaned_data.get('customer_user')
        customer_name = cleaned_data.get('customer_name')
        customer_phone = cleaned_data.get('customer_phone')
        customer_email = cleaned_data.get('customer_email')
        customer_dob = cleaned_data.get('customer_dob')
        customer_address = cleaned_data.get('customer_address')
        
        # If customer_user is not selected, ensure other fields are filled
        if not customer_user:
            if not customer_name:
                self.add_error('customer_name', 'This field is required if no customer is selected.')
            if not customer_phone:
                self.add_error('customer_phone', 'This field is required if no customer is selected.')
            if not customer_email:
                self.add_error('customer_email', 'This field is required if no customer is selected.')

        return cleaned_data
    def clean_customer_dob(self):
        customer_dob = self.cleaned_data.get('customer_dob')
        if customer_dob:
            try:
                day, month = map(int, customer_dob.split('-'))
                if day < 1 or day > 31 or month < 1 or month > 12:
                    raise forms.ValidationError("Invalid date. Please use the format DD-MM e.g. 21-03")
            except (ValueError, IndexError):
                raise forms.ValidationError("Invalid date format. Please use the format DD-MM e.g. 21-03")
        return customer_dob

class BillingItemForm(forms.ModelForm):
    medicine = forms.ModelChoiceField(queryset=MedicineModel.objects.all())

    class Meta:
        model = BillingItemModel
        fields = ['medicine', 'medicine_quantity','calculation_type']

        
class SignInForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
