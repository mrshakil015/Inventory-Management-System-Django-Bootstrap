from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(InventoryUser)
admin.site.register(EmployeeModel)
admin.site.register(CustomerModel)
admin.site.register(MedicineModel)
admin.site.register(MedicineCategoryModel)
admin.site.register(MedicineStockModel)
admin.site.register(BottleBreakageModel)
admin.site.register(OrderModel)
admin.site.register(OrderItemModel)
admin.site.register(NotificationModel)