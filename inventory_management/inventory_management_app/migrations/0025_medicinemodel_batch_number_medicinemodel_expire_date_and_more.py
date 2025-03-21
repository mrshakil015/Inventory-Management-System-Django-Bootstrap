# Generated by Django 5.1.6 on 2025-03-17 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management_app', '0024_medicinemodel_brand_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicinemodel',
            name='batch_number',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='medicinemodel',
            name='expire_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='medicinemodel',
            name='manufacturing_date',
            field=models.DateField(null=True),
        ),
    ]
