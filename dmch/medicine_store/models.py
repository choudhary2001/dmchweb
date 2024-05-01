from django.db import models
from django.contrib.auth.models import User
import datetime
import uuid
from drug.models import *
from counter.models import *

class Medicine(models.Model):
    medicine_id =  models.CharField(max_length=8, unique=True, editable=False, default="")
    product = models.ForeignKey(ProductSupply, on_delete=models.SET_NULL, blank = True, null = True)
    quantity = models. BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True,blank = True, null = True)


    def save(self, *args, **kwargs):
        if not self.medicine_id:
            self.medicine_id = str(uuid.uuid4().int)[:8]
        super(Medicine, self).save(*args, **kwargs)

    def __str__(self):
        return self.medicine_id
    

class MedicineConsumption(models.Model):
    consumption_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True)
    patient = models.ForeignKey(Patient, on_delete = models.SET_NULL, blank = True, null = True)
    products = models.ManyToManyField(Medicine, related_name='medicineconsumption_medicine')
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.consumption_id:
            self.consumption_id = str(uuid.uuid4().int)[:8]
        super(MedicineConsumption, self).save(*args, **kwargs)


    def __str__(self):
        return self.consumption_id
    
