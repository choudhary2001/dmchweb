# Generated by Django 5.0.3 on 2024-05-03 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_product_bill_date_product_bill_no_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productconsumption',
            name='indent_no',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]