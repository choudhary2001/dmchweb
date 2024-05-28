from django.db import models
from django.contrib.auth.models import User
import datetime
import uuid

class StoreDepartment(models.Model):
    department_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    name = models.CharField(max_length = 255)
    room_no = models.CharField(max_length = 255, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.department_id:
            self.department_id = str(uuid.uuid4().int)[:8]
        super(StoreDepartment, self).save(*args, **kwargs)

    def __str__(self):
        return self.name



class Product(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True)
    product_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    sdepartment = models.ForeignKey(StoreDepartment, on_delete = models.SET_NULL, blank = True, null = True)
    product_name = models.CharField(max_length = 255)
    company_name = models.CharField(max_length = 255, blank = True, null = True)
    company_address = models.CharField(max_length = 255, blank = True, null = True)
    quantity = models.BigIntegerField(blank=True, null=True)
    quantity_type =  models.CharField(max_length = 255, blank = True, null = True)
    stock_quantity = models.BigIntegerField(blank=True, null=True)
    bill_no = models.CharField(max_length = 50, blank = True, null = True)
    chalan_no = models.CharField(max_length = 50, blank = True, null = True)
    bill_date = models.DateField(blank=True, null=True)
    chalan_date = models.DateField(blank=True, null=True)
    sp_order_no = models.CharField(max_length = 50, blank = True, null = True)
    sp_order_date = models.DateField(blank=True, null=True)
    received_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product_id = str(uuid.uuid4().int)[:8]
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_id}  "

class ProductConsumption(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True)
    product_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    department = models.CharField(max_length = 255)
    indent_no = models.CharField(max_length = 255, blank = True, null = True)
    sdepartment = models.ForeignKey(StoreDepartment, on_delete = models.SET_NULL, blank = True, null = True)
    product_name = models.CharField(max_length = 255)
    company_name = models.CharField(max_length = 255)
    company_address = models.CharField(max_length = 255, blank = True, null = True)
    quantity = models.BigIntegerField(blank=True, null=True)
    quantity_type =  models.CharField(max_length = 255, blank = True, null = True)
    stock_quantity = models.BigIntegerField(blank=True, null=True)
    bill_no = models.CharField(max_length = 50, blank = True, null = True)
    chalan_no = models.CharField(max_length = 50, blank = True, null = True)
    bill_date = models.DateField(blank=True, null=True)
    chalan_date = models.DateField(blank=True, null=True)
    sp_order_no = models.CharField(max_length = 50, blank = True, null = True)
    sp_order_date = models.DateField(blank=True, null=True)
    received_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product_id = str(uuid.uuid4().int)[:8]
        super(ProductConsumption, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_id

