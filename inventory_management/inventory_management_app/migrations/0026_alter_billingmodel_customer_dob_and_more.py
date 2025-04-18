# Generated by Django 5.1.6 on 2025-03-19 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management_app', '0025_medicinemodel_batch_number_medicinemodel_expire_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingmodel',
            name='customer_dob',
            field=models.CharField(blank=True, help_text='Format: DD-MM', max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='customermodel',
            name='customer_dob',
            field=models.CharField(blank=True, help_text='Format: DD-MM', max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='medicinemodel',
            name='unit_price',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, help_text='Unit price of the product calculated by per pack size. This is the sale price', max_digits=10, null=True),
        ),
    ]
