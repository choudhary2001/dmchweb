from django.db import models
from django.contrib.auth.models import User
import datetime
import uuid
from counter.models import *
from django.utils import timezone
from datetime import timedelta

class DrugDepartment(models.Model):
    department_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    name = models.CharField(max_length = 255)
    room_no = models.CharField(max_length = 255, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.department_id:
            self.department_id = str(uuid.uuid4().int)[:8]
        super(DrugDepartment, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Suppliar(models.Model):
    suppliar_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    name = models.CharField(max_length = 255)
    mobile = models.CharField(max_length = 255, blank = True, null = True)
    gst = models.CharField(max_length = 255, blank = True, null = True)
    email = models.CharField(max_length = 255, blank = True, null = True)
    address = models.CharField(max_length = 255, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.suppliar_id:
            self.suppliar_id = str(uuid.uuid4().int)[:8]
        super(Suppliar, self).save(*args, **kwargs)



class ProductType(models.Model):
    product_type_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    name = models.CharField(max_length = 255)
    p_type = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.product_type_id:
            self.product_type_id = str(uuid.uuid4().int)[:8]
        super(ProductType, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.p_type} - {self.name}"

class ProductDetails(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL,  blank = True, null = True)
    productdetails_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    product = models.ForeignKey(ProductType, on_delete = models.SET_NULL, blank = True, null =True)
    department = models.ForeignKey(DrugDepartment, on_delete = models.SET_NULL,  blank = True, null = True)
    mfg_name = models.CharField(max_length=255, blank = True, null = True)
    batch_no = models.CharField(max_length=255, blank = True, null = True)
    stock_quantity = models.BigIntegerField(blank=True, null=True)
    quantity = models.BigIntegerField(blank=True, null=True)
    mfg_date = models.DateField(blank=True, null=True)
    exp_date = models.DateField(blank=True, null=True)
    mrp = models.BigIntegerField(blank=True, null=True)
    purchase_rate = models.BigIntegerField(blank=True, null=True)
    purchase_amount = models.BigIntegerField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    supply_date = models.DateField(blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.productdetails_id:
            self.productdetails_id = str(uuid.uuid4().int)[:8]
        super(ProductDetails, self).save(*args, **kwargs)

class ProductPurchase(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True)
    productdetails_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    product = models.ForeignKey(ProductType, on_delete = models.SET_NULL, blank = True, null = True)
    product_name = models.CharField(max_length = 255, blank = True, null = True)
    product_type = models.CharField(max_length = 255, blank = True, null = True)
    department = models.ForeignKey(DrugDepartment, on_delete = models.SET_NULL, blank = True, null = True)
    mfg_name = models.CharField(max_length=255, blank = True, null = True)
    batch_no = models.CharField(max_length=255)
    stock_quantity = models.BigIntegerField(blank=True, null=True)
    quantity = models.BigIntegerField(blank=True, null=True)
    mfg_date = models.DateField(blank=True, null=True)
    exp_date = models.DateField(blank=True, null=True)
    mrp = models.BigIntegerField(blank=True, null=True)
    purchase_rate = models.BigIntegerField(blank=True, null=True)
    purchase_amount = models.BigIntegerField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    supply_date = models.DateField(blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.productdetails_id:
            self.productdetails_id = str(uuid.uuid4().int)[:8]
        super(ProductPurchase, self).save(*args, **kwargs)

    def is_expiring_soon(self):
        """
        Check if the product is expiring within 3 months from today.
        """
        today = timezone.now().date()
        three_months_from_today = today + timedelta(days=3*30)  # Assuming a month has 30 days
        return self.exp_date is not None and today <= self.exp_date <= three_months_from_today

    @staticmethod
    def get_expiring_products():
        """
        Get a queryset of products that are expiring within 3 months from today.
        """
        today = timezone.now().date()
        three_months_from_today = today + timedelta(days=3*30)  # Assuming a month has 30 days
        return ProductPurchase.objects.filter(exp_date__isnull=False, exp_date__range=(today, three_months_from_today))


class ProductSupply(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True)
    productdetails_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    product_name = models.CharField(max_length = 255, blank = True, null = True)
    product_type = models.CharField(max_length = 255, blank = True, null = True)
    product = models.ForeignKey(ProductType, on_delete = models.SET_NULL,  blank = True, null = True)
    department = models.ForeignKey(DrugDepartment, on_delete = models.SET_NULL,  blank = True, null = True)
    mfg_name = models.CharField(max_length=255, blank = True, null = True)
    batch_no = models.CharField(max_length=255, blank = True, null = True)
    stock_quantity = models.BigIntegerField(blank=True, null=True)
    quantity = models.BigIntegerField(blank=True, null=True)
    mfg_date = models.DateField(blank=True, null=True)
    exp_date = models.DateField(blank=True, null=True)
    mrp = models.BigIntegerField(blank=True, null=True)
    purchase_rate = models.BigIntegerField(blank=True, null=True)
    purchase_amount = models.BigIntegerField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    supply_date = models.DateField(blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    remarks = models.CharField(max_length = 255, blank = True, null = True, default="")

    def save(self, *args, **kwargs):
        if not self.productdetails_id:
            self.productdetails_id = str(uuid.uuid4().int)[:8]
        super(ProductSupply, self).save(*args, **kwargs)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL,  blank = True, null = True)
    ord_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    order_id = models.CharField(max_length=20)
    supplier = models.ForeignKey(Suppliar, on_delete = models.SET_NULL, blank = True, null =True)
    mob_no = models.CharField(max_length=20, blank = True, null = True)
    gst = models.CharField(max_length=20, blank = True, null = True)
    email = models.CharField(max_length=80, blank = True, null = True)
    order_date = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(ProductDetails, related_name='order_products')

    def save(self, *args, **kwargs):
        if not self.ord_id:
            self.ord_id = str(uuid.uuid4().int)[:8]
        super(Order, self).save(*args, **kwargs)

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True)
    purchase_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    order_id = models.CharField(max_length=20)
    supplier = models.ForeignKey(Suppliar, on_delete = models.SET_NULL, blank = True, null =True)
    mob_no = models.CharField(max_length=20, blank = True, null = True)
    gst = models.CharField(max_length=20, blank = True, null = True)
    email = models.CharField(max_length=80, blank = True, null = True)
    invoice_no = models.CharField(max_length=75)
    invoice_date = models.DateField()
    total_amount = models.BigIntegerField( blank=True, null=True)
    paid = models.BigIntegerField(blank=True, null=True)
    due = models.BigIntegerField(blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(ProductPurchase, related_name='purchase_products')

    def save(self, *args, **kwargs):
        if not self.purchase_id:
            self.purchase_id = str(uuid.uuid4().int)[:8]
        super(Purchase, self).save(*args, **kwargs)


class Supply(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL,  blank = True, null = True)
    supply_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    indent = models.CharField(max_length=20, blank = True, null = True)
    departpment = models.ForeignKey(DrugDepartment, on_delete = models.SET_NULL,  blank = True, null = True)
    products = models.ManyToManyField(ProductSupply, related_name='supply_products')
    total_quantity = models.IntegerField(blank = True, null = True)
    quantity = models.IntegerField(blank = True, null = True)
    de = models.CharField(max_length = 100, blank = True, null = True, default=None)
    remarks = models.CharField(max_length = 255, blank = True, null = True, default="")
    order_date = models.DateTimeField(blank = True, null = True,)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.supply_id:
            self.supply_id = str(uuid.uuid4().int)[:8]
        super(Supply, self).save(*args, **kwargs)

