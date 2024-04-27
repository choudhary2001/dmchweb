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
    company_name = models.CharField(max_length = 255)
    quantity = models.BigIntegerField(blank=True, null=True)
    stock_quantity = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product_id = str(uuid.uuid4().int)[:8]
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_id

class ProductConsumption(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True)
    product_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    department = models.CharField(max_length = 255)
    sdepartment = models.ForeignKey(StoreDepartment, on_delete = models.SET_NULL, blank = True, null = True)
    product_name = models.CharField(max_length = 255)
    company_name = models.CharField(max_length = 255)
    quantity = models.BigIntegerField(blank=True, null=True)
    stock_quantity = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product_id = str(uuid.uuid4().int)[:8]
        super(ProductConsumption, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_id