# Generated by Django 5.1.6 on 2025-03-05 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management_app', '0016_alter_billingitemmodel_medicine_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicinemodel',
            name='total_case_pack',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='medicinemodel',
            name='total_medicine',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True),
        ),
    ]
