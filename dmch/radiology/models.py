from django.db import models
from django.contrib.auth.models import User
import datetime
import uuid

class RadiologyDepartment(models.Model):
    department_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    name = models.CharField(max_length = 255)
    room_no = models.CharField(max_length = 255, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.department_id:
            self.department_id = str(uuid.uuid4().int)[:8]
        super(RadiologyDepartment, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Investigation(models.Model):
    investigation_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    name = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.investigation_id:
            self.investigation_id = str(uuid.uuid4().int)[:8]
        super(Investigation, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    


class RadiologyDoctor(models.Model):
    doctor_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    department = models.ForeignKey(RadiologyDepartment, on_delete = models.SET_NULL, blank = True, null = True)
    name = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.doctor_id:
            self.doctor_id = str(uuid.uuid4().int)[:8]
        super(RadiologyDoctor, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Radiology(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True)
    radiology_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    patient_name = models.CharField(max_length = 255, blank = True, null = True)
    reg_no = models.CharField(max_length = 255, blank = True, null = True)
    doctor = models.ForeignKey(RadiologyDoctor, on_delete = models.SET_NULL,  blank = True, null = True)
    department = models.ForeignKey(RadiologyDepartment, on_delete = models.SET_NULL,  blank = True, null = True)
    investigation = models.ForeignKey(Investigation, on_delete = models.SET_NULL,  blank = True, null = True)
    investigation_unit = models.CharField(max_length = 255, blank = True, null = True)
    patient_type = models.CharField(max_length = 255, blank = True, null = True)
    investigation_type = models.CharField(max_length = 255, blank = True, null = True)
    no_of_plate = models.CharField(max_length = 255, blank = True, null = True)
    plate_size = models.CharField(max_length = 255, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.radiology_id:
            self.radiology_id = str(uuid.uuid4().int)[:8]
        super(Radiology, self).save(*args, **kwargs)

    def __str__(self):
        return self.patient_name

