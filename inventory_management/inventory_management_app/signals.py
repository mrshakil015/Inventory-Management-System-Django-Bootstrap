# inventory_management_app/signals.py
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import MedicineModel, NotificationModel, BottleBreakageModel

@receiver(post_save, sender=MedicineModel)
def check_stock_and_notify(sender, instance, created, **kwargs):
    if created:
        return

    try:
        previous_instance = MedicineModel.objects.get(id=instance.id)
    except MedicineModel.DoesNotExist:
        return 

    # Check if the stock has been updated and is now below the threshold
    if previous_instance.total_case_pack != instance.total_case_pack and instance.total_case_pack < 10:
        subject = f"Low Stock Alert: {instance.medicine_name}"
        message = (
            f"The stock for medicine '{instance.medicine_name}' is low.\n"
            f"Current Total Pack of Medicine: {instance.total_case_pack}\n"
            f"Please restock immediately!"
        )
        recipient_list = ['shakil@ethicalden.com']
        
        # Send an email notification
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        # Save the notification to the NotificationModel
        for recipient in recipient_list:
            NotificationModel.objects.create(
                title=subject,
                message=message,
                recipient=recipient
            )
                
@receiver(post_save, sender=BottleBreakageModel)
def bottle_breakage_alert(sender, instance, **kwargs):
    if instance.lost_quantity > 0:
        subject = f"Bottle Breakage Alert: {instance.medicine.medicine_name}"
        message = (
            f"A breakage has been reported for the medicine '{instance.medicine.medicine_name}'.\n"
            f"Lost Quantity: {instance.lost_quantity} Pack\n"
            f"Date: {instance.date_time}\n"
            f"Reason: {instance.reason if instance.reason else 'No reason provided'}\n"
            f"Responsible Employee: {instance.responsible_employee.employee_user}\n"
        )
        recipient_list = ['shakil@ethicalden.com']
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        # Save to NotificationModel
        for recipient in recipient_list:
            NotificationModel.objects.create(
                title=subject,
                message=message,
                recipient=recipient
            )