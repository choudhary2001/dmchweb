from django.db import models
from counter.models import *
from django.contrib.auth.models import User


class PathologyDepartment(models.Model):
    department_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    name = models.CharField(max_length = 255)
    room_no = models.CharField(max_length = 255, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.department_id:
            self.department_id = str(uuid.uuid4().int)[:8]
        super(PathologyDepartment, self).save(*args, **kwargs)

    def __str__(self):
        return self.name



class PathologyDoctor(models.Model):
    doctor_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    name = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.doctor_id:
            self.doctor_id = str(uuid.uuid4().int)[:8]
        super(PathologyDoctor, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Testcode(models.Model):
    test_code = models.CharField(max_length=200, unique = True)
    test_name = models.CharField(max_length=200)

class Patient_registration(models.Model):
    patient_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    department = models.ForeignKey(PathologyDepartment, on_delete = models.CASCADE, blank = True, null = True)
    date = models.DateField()
    bill_no = models.PositiveIntegerField(unique=True)
    lab_no = models.CharField(max_length = 200, blank = True, null = True)
    patient_name = models.CharField(max_length = 200, blank = True, null = True)
    gender = models.CharField(max_length = 200, blank = True, null = True)
    age = models.CharField(max_length = 200, blank = True, null = True)
    reg_no = models.ForeignKey(Patient, on_delete = models.CASCADE)
    referby = models.ForeignKey(PathologyDoctor, on_delete = models.CASCADE, blank = True, null = True)
    test_name = models.CharField(max_length = 255, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = str(uuid.uuid4().int)[:8]
        if not self.bill_no: 
            last_patient_pp = Patient_registration.objects.order_by('-created_at').first()
            if last_patient_pp:
                bill_no = int(last_patient_pp.bill_no) + 1
            else:
                bill_no = 1
            self.bill_no = bill_no
        super(Patient_registration, self).save(*args, **kwargs)


class Test_report(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    test_report_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    reg_no = models.ForeignKey(Patient, on_delete = models.CASCADE)
    patient = models.ForeignKey(Patient_registration, on_delete = models.CASCADE)
    palsma_glucose_fasting = models.CharField(max_length = 200, blank = True, null = True)
    palsma_glucose_pp = models.CharField(max_length = 200, blank = True, null = True)
    blood_sugar_random = models.CharField(max_length = 200, blank = True, null = True)
    blood_ures = models.CharField(max_length = 200, blank = True, null = True)
    serun_creatinine = models.CharField(max_length = 200, blank = True, null = True)
    serum_uric_acid = models.CharField(max_length = 200, blank = True, null = True)
    billirubin_total = models.CharField(max_length = 200, blank = True, null = True)
    sgpt = models.CharField(max_length = 200, blank = True, null = True)
    sgot = models.CharField(max_length = 200, blank = True, null = True)
    total_protein = models.CharField(max_length = 200, blank = True, null = True)
    serum_albumin = models.CharField(max_length = 200, blank = True, null = True)
    alk_phosphatase = models.CharField(max_length = 200, blank = True, null = True)
    gama_gt = models.CharField(max_length = 200, blank = True, null = True)
    amylase = models.CharField(max_length = 200, blank = True, null = True)
    hbaic = models.CharField(max_length = 200, blank = True, null = True)
    total_cholestrol = models.CharField(max_length = 200, blank = True, null = True)
    hdl_cholestrol = models.CharField(max_length = 200, blank = True, null = True)
    ldl_cholestrol = models.CharField(max_length = 200, blank = True, null = True)
    vldl_cholestrol = models.CharField(max_length = 200, blank = True, null = True)
    serum_trigicerides = models.CharField(max_length = 200, blank = True, null = True)
    serun_sodium = models.CharField(max_length = 200, blank = True, null = True)
    serum_potasium = models.CharField(max_length = 200, blank = True, null = True)
    serum_cloried = models.CharField(max_length = 200, blank = True, null = True)
    serum_calcium = models.CharField(max_length = 200, blank = True, null = True)
    aso_titer = models.CharField(max_length = 200, blank = True, null = True)
    crp = models.CharField(max_length = 200, blank = True, null = True)
    raf_factor = models.CharField(max_length = 200, blank = True, null = True)
    lipase = models.CharField(max_length = 200, blank = True, null = True)
    esr = models.CharField(max_length = 200, blank = True, null = True)
    bt = models.CharField(max_length = 200, blank = True, null = True)
    ct = models.CharField(max_length = 200, blank = True, null = True)
    cbc = models.CharField(max_length = 200, blank = True, null = True)
    lth = models.CharField(max_length = 200, blank = True, null = True)
    other = models.CharField(max_length = 250, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.test_report_id:
            self.test_report_id = str(uuid.uuid4().int)[:8]
        super(Test_report, self).save(*args, **kwargs)


class Urine_test(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    urinetest_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    reg_no = models.ForeignKey(Patient, on_delete = models.CASCADE)
    patient = models.ForeignKey(Patient_registration, on_delete = models.CASCADE)
    amount = models.CharField(max_length = 200, blank = True, null = True)
    colour = models.CharField(max_length = 200, blank = True, null = True)
    odour = models.CharField(max_length = 200, blank = True, null = True)
    specific_gravity = models.CharField(max_length = 200, blank = True, null = True)
    deposti = models.CharField(max_length = 200, blank = True, null = True)
    reaction = models.CharField(max_length = 200, blank = True, null = True)
    sugar = models.CharField(max_length = 200, blank = True, null = True)
    albumin = models.CharField(max_length = 200, blank = True, null = True)
    phosphate = models.CharField(max_length = 200, blank = True, null = True)
    mucin = models.CharField(max_length = 200, blank = True, null = True)
    bile_salt = models.CharField(max_length = 200, blank = True, null = True)
    bile_pigment = models.CharField(max_length = 200, blank = True, null = True)
    urobilinogen = models.CharField(max_length = 200, blank = True, null = True)
    acetone_bodies = models.CharField(max_length = 200, blank = True, null = True)
    rbc = models.CharField(max_length = 200, blank = True, null = True)
    wbc = models.CharField(max_length = 200, blank = True, null = True)
    epitheilal_cell = models.CharField(max_length = 200, blank = True, null = True)
    casts = models.CharField(max_length = 200, blank = True, null = True)
    crystas = models.CharField(max_length = 200, blank = True, null = True)
    others = models.CharField(max_length = 200, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.urinetest_id:
            self.urinetest_id = str(uuid.uuid4().int)[:8]
        super(Urine_test, self).save(*args, **kwargs)


class Stool_test(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    stool_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    reg_no = models.ForeignKey(Patient, on_delete = models.CASCADE)
    patient = models.ForeignKey(Patient_registration, on_delete = models.CASCADE)
    colour = models.CharField(max_length = 200, blank = True, null = True)
    odour = models.CharField(max_length = 200, blank = True, null = True)
    consistency = models.CharField(max_length = 200, blank = True, null = True)
    ocalt_blood = models.CharField(max_length = 200, blank = True, null = True)
    reducing_sugar = models.CharField(max_length = 200, blank = True, null = True)
    chemical_reaction = models.CharField(max_length = 200, blank = True, null = True)
    ova_roundword = models.CharField(max_length = 200, blank = True, null = True)
    ova_hookworm = models.CharField(max_length = 200, blank = True, null = True)
    ova_threadworm = models.CharField(max_length = 200, blank = True, null = True)
    ova_tenia = models.CharField(max_length = 200, blank = True, null = True)
    ova_tt = models.CharField(max_length = 200, blank = True, null = True)
    eh_cyst = models.CharField(max_length = 200, blank = True, null = True)
    ecoli_cyst = models.CharField(max_length = 200, blank = True, null = True)
    girida_lamba_cyst = models.CharField(max_length = 200, blank = True, null = True)
    wbc = models.CharField(max_length = 200, blank = True, null = True)
    rbc = models.CharField(max_length = 200, blank = True, null = True)
    others = models.CharField(max_length = 200, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.stool_id:
            self.stool_id = str(uuid.uuid4().int)[:8]
        super(Stool_test, self).save(*args, **kwargs)



class Ctest_report(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    cttest_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    reg_no = models.ForeignKey(Patient, on_delete = models.CASCADE)
    patient = models.ForeignKey(Patient_registration, on_delete = models.CASCADE)
    volume = models.CharField(max_length = 200, blank = True, null = True)
    consistency = models.CharField(max_length = 200, blank = True, null = True)
    colour = models.CharField(max_length = 200, blank = True, null = True)
    abestinenece = models.CharField(max_length = 200, blank = True, null = True)
    time_exam = models.CharField(max_length = 200, blank = True, null = True)
    method_collection = models.CharField(max_length = 200, blank = True, null = True)
    total_count = models.CharField(max_length = 200, blank = True, null = True)
    active = models.CharField(max_length = 200, blank = True, null = True)
    sluggish = models.CharField(max_length = 200, blank = True, null = True)
    non_matliz = models.CharField(max_length = 200, blank = True, null = True)
    rbc = models.CharField(max_length = 200, blank = True, null = True)
    wbc = models.CharField(max_length = 200, blank = True, null = True)
    epithelial_cells = models.CharField(max_length = 200, blank = True, null = True)
    abnormality = models.CharField(max_length = 200, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.cttest_id:
            self.cttest_id = str(uuid.uuid4().int)[:8]
        super(Ctest_report, self).save(*args, **kwargs)


class Cbc_test(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    cbctest_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    reg_no = models.ForeignKey(Patient, on_delete = models.CASCADE)
    patient = models.ForeignKey(Patient_registration, on_delete = models.CASCADE)
    rbc = models.CharField(max_length = 200, blank = True, null = True)
    hgb = models.CharField(max_length = 200, blank = True, null = True)
    hct = models.CharField(max_length = 200, blank = True, null = True)
    mcv = models.CharField(max_length = 200, blank = True, null = True)
    mch = models.CharField(max_length = 200, blank = True, null = True)
    mchc = models.CharField(max_length = 200, blank = True, null = True)
    rdw_sd = models.CharField(max_length = 200, blank = True, null = True)
    rdw_cv = models.CharField(max_length = 200, blank = True, null = True)
    wbc = models.CharField(max_length = 200, blank = True, null = True)
    neut = models.CharField(max_length = 200, blank = True, null = True)
    lymph = models.CharField(max_length = 200, blank = True, null = True)
    mono = models.CharField(max_length = 200, blank = True, null = True)
    eo = models.CharField(max_length = 200, blank = True, null = True)
    baso = models.CharField(max_length = 200, blank = True, null = True)
    plt = models.CharField(max_length = 200, blank = True, null = True)
    pdw = models.CharField(max_length = 200, blank = True, null = True)
    mpv = models.CharField(max_length = 200, blank = True, null = True)
    p_lcr = models.CharField(max_length = 200, blank = True, null = True)
    pct = models.CharField(max_length = 200, blank = True, null = True)
    ret = models.CharField(max_length = 200, blank = True, null = True)
    irf = models.CharField(max_length = 200, blank = True, null = True)
    lfr = models.CharField(max_length = 200, blank = True, null = True)
    mfr = models.CharField(max_length = 200, blank = True, null = True)
    hfr = models.CharField(max_length = 200, blank = True, null = True)
    wbc_ip_message = models.CharField(max_length = 200, blank = True, null = True)
    rcb_rft_ip_message = models.CharField(max_length = 200, blank = True, null = True)
    plt_ip_message = models.CharField(max_length = 200, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)
    

    def save(self, *args, **kwargs):
        if not self.cbctest_id:
            self.cbctest_id = str(uuid.uuid4().int)[:8]
        super(Cbc_test, self).save(*args, **kwargs)


class Serology_test(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    strology_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    reg_no = models.ForeignKey(Patient, on_delete = models.CASCADE)
    patient = models.ForeignKey(Patient_registration, on_delete = models.CASCADE, blank = True, null = True)

    hiv = models.CharField(max_length = 200, blank = True, null = True)
    hcv = models.CharField(max_length = 200, blank = True, null = True)
    hbsag = models.CharField(max_length = 200, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.strology_id:
            self.strology_id = str(uuid.uuid4().int)[:8]
        super(Serology_test, self).save(*args, **kwargs)


