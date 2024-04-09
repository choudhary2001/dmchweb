from django.db import models
from django.contrib.auth.models import User
import datetime
import uuid

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_role = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add=True)

class Department(models.Model):
    department_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    name = models.CharField(max_length = 255)
    room_no = models.CharField(max_length = 255, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.department_id:
            self.department_id = str(uuid.uuid4().int)[:8]
        super(Department, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    


class Doctor(models.Model):
    doctor_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank = True, null = True)
    name = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.doctor_id:
            self.doctor_id = str(uuid.uuid4().int)[:8]
        super(Doctor, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Patient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    regno = models.CharField(max_length=100, primary_key = True, unique = True)
    regnoid = models.CharField(max_length=100)
    uhidno = models.CharField(max_length=100)
    uhidnoincre = models.CharField(max_length=100)
    redcard = models.BooleanField(default=False)
    redcardid = models.CharField(max_length=255, blank=True, null=True)
    redcardtype = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    guardiannametitle = models.CharField(max_length=100)
    guardianname = models.CharField(max_length=255)
    year = models.IntegerField(blank = True, null = True)
    month = models.IntegerField(blank = True, null = True)
    days = models.IntegerField(blank = True, null = True)
    gender = models.CharField(max_length=10)
    mobno = models.CharField(max_length=20)
    address = models.TextField()
    district = models.CharField(max_length=100)
    policest = models.CharField(max_length=100, blank = True, null = True)
    state = models.CharField(max_length=100, blank = True, null = True)
    pincode = models.CharField(max_length=20, blank = True, null = True)
    symptoms = models.TextField()
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, blank = True, null = True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank = True, null = True)
    visittype = models.CharField(max_length=100)
    appointment_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.regnoid:  # Check if regnoid is not already set
            current_year = datetime.datetime.now().year % 100  # Get last two digits of the current year
            self.regnoid = f'DH{current_year}'
            
        if not self.regno:  # Check if regno is not already set
            last_patient_pp = Patient.objects.order_by('-appointment_date').first()
            if last_patient_pp:
                regno = int(last_patient_pp.regno) + 1
            else:
                regno = 1

            while Patient.objects.filter(regno=regno).exists():
                regno += 1
            self.regno = regno
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.regno}"

