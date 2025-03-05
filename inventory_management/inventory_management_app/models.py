from django.db import models
from django.contrib.auth.models import AbstractUser
from autoslug import AutoSlugField

# Create your models here.
class InventoryUser(AbstractUser):
    ROLE = [
        ('Admin','Admin'),
        ('Inventory Manager','Inventory Manager'),
        ('Billing Staff','Billing Staff'),
    ]
    role = models.CharField(choices=ROLE,max_length=20,null=True)
    user_access_list = models.TextField(blank=True, null=True)
    
    def get_user_access_list(self):
        """Convert stored string back to a list"""
        return self.user_access_list.split(',') if self.user_access_list else []
    
    def __str__(self):
        return self.username
    
class EmployeeModel(models.Model):
    employee_user = models.OneToOneField(InventoryUser, on_delete=models.CASCADE, null=True)
    employee_id = models.CharField(max_length=20, null=True)
    employee_name = models.CharField(max_length=50, null=True)
    employee_contact = models.CharField(max_length=15, null=True)
    employee_address = models.CharField(max_length=255, null=True)
    employee_picture = models.ImageField(upload_to='employee/', blank=True, null=True)
    created_by = models.ForeignKey(InventoryUser, on_delete=models.SET_NULL, null=True, related_name="employee_added")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.employee_name
    
#------customer model    
class CustomerModel(models.Model):    
    customer_name = models.CharField(max_length=50,null=True, blank=True)
    customer_phone = models.CharField(max_length=15, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    customer_dob = models.DateField(null=True, blank=True)
    customer_address = models.CharField(max_length=255,null=True, blank=True)
    created_by = models.ForeignKey(InventoryUser, on_delete=models.CASCADE,null=True, related_name="customer_added")
    created_at = models.DateField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.customer_phone if self.customer_phone else "Unknown Customer"


class MedicineCategoryModel(models.Model):
    category_name = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return self.category_name

class MedicineUnitModel(models.Model):
    unit_name = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return self.unit_name
    
class MedicineModel(models.Model):
    MEDICINE_TYPES = [
        ('Liquids','Liquids'),
        ('Solids','Solids'),
    ]
    STOCK_STATUS =[
        ('Available','Available'),
        ('Out of Stock','Out of Stock'),
    ]
    medicine_name = models.CharField(max_length=100, null=True)
    sku = models.CharField(max_length=50, null=True)
    slug = AutoSlugField(populate_from='medicine_name', unique=True,null=True)
    medicine_category = models.ForeignKey(MedicineCategoryModel, on_delete=models.CASCADE,null=True, related_name='medicine_category')
    medicine_type = models.CharField(choices=MEDICINE_TYPES, max_length=10, null=True)
    pack_units = models.ForeignKey(MedicineUnitModel, on_delete=models.CASCADE,null=True, related_name='medicine_unit')
    description = models.TextField(blank=True, null=True)
    medicine_picture = models.ImageField(upload_to='medicines/', blank=True, null=True)
    pack_size = models.PositiveIntegerField(default=0,null=True,help_text="Pack size unit must be the ml/gm/x.")
    total_case_pack = models.DecimalField(max_digits=10, decimal_places=2, blank=True,default=0,null=True)
    total_medicine = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True, blank=True)
    stocks = models.CharField(choices=STOCK_STATUS,max_length=20, default='Out of Stock',null=True)
    unit_price = models.FloatField(default=0,null=True,blank=True,help_text="Unit price of the product calculated by per per pack size. This is the sale price")
    created_by = models.ForeignKey(InventoryUser, on_delete=models.CASCADE,null=True, related_name="medicine_added")
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def update_stock_status(self):
        if self.total_case_pack is None or self.total_case_pack <= 0:
            self.stocks = 'Out of Stock'
        else:
            self.stocks = 'Available'
    def calculate_total_medicine(self):
        if self.pack_size is not None or self.total_case_pack is not None:
            self.total_medicine = self.pack_size * self.total_case_pack
        else:
            self.total_medicine = 0
            
    def save(self, *args, **kwargs):
        self.update_stock_status()
        self.calculate_total_medicine()
        super().save(*args, **kwargs)
    
    
    def __str__(self):
        return self.medicine_name
    
class MedicineStockModel(models.Model):
    medicine = models.ForeignKey(MedicineModel, on_delete=models.CASCADE,related_name='medicinestocks',null=True)
    total_case_pack = models.PositiveIntegerField(default=0,null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True,help_text="Unit price of per pack")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    created_by = models.ForeignKey(InventoryUser, on_delete=models.CASCADE,null=True, related_name="stock_added")
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_total(self):
        return self.total_case_pack * self.purchase_price
    
    def save(self, *args, **kwargs):
        
        self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.medicine.medicine_name
    
class BottleBreakageModel(models.Model):
    medicine = models.ForeignKey(MedicineModel, on_delete=models.CASCADE,related_name='breakages',null=True)
    lost_quantity = models.PositiveIntegerField(default=0,help_text="Lost the no of case pack",null=True)
    date_time = models.DateField(null=True)
    reason = models.TextField(blank=True, null=True)
    responsible_employee = models.ForeignKey(EmployeeModel, on_delete=models.CASCADE,null=True)
    created_by = models.ForeignKey(InventoryUser, on_delete=models.CASCADE,null=True, related_name="breakage_added")
    
    def __str__(self):
        return self.medicine.medicine_name
    
class BillingModel(models.Model):    
    BILLING_STATUS = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    ]
    
    billing_no = models.CharField(max_length=20, null=True, unique=True)
    
    customer_user = models.ForeignKey(CustomerModel, on_delete=models.SET_NULL, null=True, blank=True, help_text='If Customer already has an account, select the customer.')
    customer_name = models.CharField(max_length=50, null=True, blank=True)
    customer_phone = models.CharField(max_length=15, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    tax_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True) 
    tax_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True) 
    discount_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True, help_text='Mention the number of percentage discount.') 
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True)
    billing_status = models.CharField(choices=BILLING_STATUS, max_length=20, default='Progress', null=True)
    created_by = models.ForeignKey(InventoryUser, on_delete=models.CASCADE, null=True, related_name="billing_added")
    billing_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)

    def __str__(self):
        return f"Billing {self.billing_no} - {self.customer_name}"


class BillingItemModel(models.Model):
    CALCULATION_TYPE_CHOICES = [
        ('Pack', 'Pack'),
        ('Unit', 'Unit'),
    ]
    
    billing = models.ForeignKey(BillingModel, on_delete=models.CASCADE, related_name='billing_items')
    medicine = models.ForeignKey(MedicineModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='medicine_billings')
    medicine_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    calculation_type = models.CharField(max_length=10, choices=CALCULATION_TYPE_CHOICES, default='Unit', null=True, blank=True)  # New field
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    def __str__(self):
        return f"{self.medicine.medicine_name if self.medicine else 'Deleted Medicine'} - {self.billing.billing_no}"

class NotificationModel(models.Model):
    title = models.CharField(max_length=255,null=True)
    message = models.TextField(null=True)
    recipient = models.EmailField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.recipient}"
