from django.db import models
from django.contrib.auth.models import AbstractUser
from autoslug import AutoSlugField

# Create your models here.
class InventoryUser(AbstractUser):
    ROLE = [
        ('Admin','Admin'),
        ('Staff','Staff'),
        ('Inventory Manager','Inventory Manager'),
        ('Billing Staff','Billing Staff'),
    ]
    role = models.CharField(choices=ROLE,max_length=20,null=True)
    def __str__(self):
        return self.username
    
class EmployeeModel(models.Model):
    employee_user = models.OneToOneField(InventoryUser,on_delete=models.CASCADE,max_length=10, null=True)
    employee_id = models.CharField(max_length=20,null=True)
    employee_name = models.CharField(max_length=20,null=True)
    employee_contact = models.CharField(max_length=15, null=True)
    employee_address = models.CharField(max_length=255,null=True)
    employee_picture = models.ImageField(upload_to='employee/', blank=True, null=True)
    created_by = models.ForeignKey(InventoryUser, on_delete=models.CASCADE,null=True, related_name="employee_added")
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    
    def __str__(self):
        return self.employee_name
    
#------customer model    
class CustomerModel(models.Model):    
    customer_name = models.CharField(max_length=20,null=True)
    customer_phone = models.CharField(max_length=15, null=True)
    customer_email = models.EmailField(null=True)
    customer_address = models.CharField(max_length=255,null=True)
    created_by = models.ForeignKey(InventoryUser, on_delete=models.CASCADE,null=True, related_name="customer_added")
    created_at = models.DateField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.customer_phone

class MedicineCategoryModel(models.Model):
    category_name = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return self.category_name
    
class MedicineModel(models.Model):
    MEDICINE_TYPES = [
        ('Liquids','Lliquids'),
        ('Solids','Solids'),
    ]
    STOCK_STATUS =[
        ('Available','Available'),
        ('Out of Stock','Out of Stock'),
    ]
    medicine_name = models.CharField(max_length=100, null=True,help_text="Mention the Bottle name with the Pack Size. Example: ALKATON 100ml")
    slug = AutoSlugField(populate_from='medicine_name', unique=True,null=True)
    medicine_category = models.ForeignKey(MedicineCategoryModel, on_delete=models.CASCADE,null=True, related_name='medicine_category')
    medicine_type = models.CharField(choices=MEDICINE_TYPES, max_length=10, null=True,help_text='Select Medicine Type')
    description = models.TextField(blank=True)
    medicine_picture = models.ImageField(upload_to='medicines/', blank=True, null=True)
    pack_size = models.DecimalField(max_digits=10, default=0,decimal_places=2,blank=True,null=True,help_text="Pack size unit must be the ml/gm.")
    total_case_pack = models.PositiveIntegerField(blank=True,default=0,null=True)
    stocks = models.CharField(choices=STOCK_STATUS,max_length=20, default='Available',null=True)
    unit_price = models.FloatField(default=0,null=True,blank=True,help_text="Unit price of the product calculated by per per pack size. This is the sale price")
    created_by = models.ForeignKey(InventoryUser, on_delete=models.CASCADE,null=True, related_name="medicine_added")
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def update_stock_status(self):
        if self.total_case_pack is None or self.total_case_pack <= 0:
            self.stocks = 'Out of Stock'
        else:
            self.stocks = 'Available'
            
    def save(self, *args, **kwargs):
        self.update_stock_status()
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
    
class OrderModel(models.Model):
    ORDER_STATUS = [
        ('Progress', 'Progress'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    order_no = models.CharField(max_length=10, null=True, unique=True)
    customer_user = models.ForeignKey(CustomerModel, on_delete=models.CASCADE, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    tax = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True)  # Moved here
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True)  # Moved here
    order_status = models.CharField(choices=ORDER_STATUS, max_length=20, default='Progress', null=True)
    created_by = models.ForeignKey(InventoryUser, on_delete=models.CASCADE,null=True, related_name="order_added")
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_no} - {self.customer_user.customer_name}"


class OrderItemModel(models.Model):
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name='order_items')
    medicine = models.ForeignKey(MedicineModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='medicine_orders')
    medicine_quantity = models.IntegerField(default=0, null=True, help_text="Add the Medicine quantity into ml/gm")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)  # Excluding tax/discount

    def __str__(self):
        return f"{self.medicine.medicine_name if self.medicine else 'Deleted Medicine'} - {self.order.order_no}"


class NotificationModel(models.Model):
    title = models.CharField(max_length=255,null=True)
    message = models.TextField(null=True)
    recipient = models.EmailField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.recipient}"
