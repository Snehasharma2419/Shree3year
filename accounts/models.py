from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^[1-9]\d{9}$',
    message="Phone number must be 10 digits and cannot start with 0."
)

class Worker(models.Model):
    ...
    phone_number = models.CharField(
        max_length=10,
        validators=[phone_validator],
        blank=True,
        null=True
    )
    
class Warden(models.Model):
    ...
    phone_number = models.CharField(
        max_length=10,
        validators=[phone_validator],
        blank=True,
        null=True
    )

# -------------------------
# CUSTOM USER MODEL
# -------------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('warden', 'Warden'),
        ('worker', 'Worker'),
        ('supplier', 'Supplier'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    university_id = models.CharField(max_length=50, unique=True)
    security_question = models.CharField(max_length=255, null=True, blank=True)
    security_answer = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

# -------------------------
# PRE-STORED UNIVERSITY IDS (Updated)
# -------------------------
class UniversityID(models.Model):
    # Role choices se 'supplier' hata diya taaki master table clean rahe
    ROLE_CHOICES = (
        ('warden', 'Warden'),
        ('worker', 'Worker'),
    )
    university_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.university_id} - {self.full_name}"

# -------------------------
# PROFILE TABLES (Updated Supplier)
# -------------------------
class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    # University record ki ab link ki zarurat nahi kyunki ye manual entry hai
    supplier_id = models.CharField(max_length=20, unique=True, default="KUTIR001")
    name = models.CharField(max_length=100, default="Kutir Supplies")
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=10, null=True, blank=True)
    
    # Ye niche wala part insure karega ki database mein sirf 1 hi row rahe
    def save(self, *args, **kwargs):
        if not self.pk and Supplier.objects.exists():
            # Agar pehle se ek supplier hai, toh naya save nahi hone dega
            return 
        super(Supplier, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (Fixed Supplier)"

class Warden(models.Model):
    # Fixed: Linked to User AND UniversityID for data integrity
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) 
    university_record = models.OneToOneField(UniversityID, on_delete=models.CASCADE, null=True, limit_choices_to={'role': 'warden'})
    warden_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=20)
    admin_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_wardens')
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    leave_balance = models.IntegerField(default=15)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.warden_id})"
    
    

class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    university_record = models.OneToOneField(UniversityID, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'role': 'worker'})
    worker_id = models.CharField(max_length=20, unique=True, blank=True) # blank=True zaroori hai
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=10, validators=[phone_validator], blank=True, null=True)
    admin_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_workers')
    is_approved = models.BooleanField(default=False)
    leave_balance = models.IntegerField(default=15)
    
    def save(self, *args, **kwargs):
        # 🟢 AUTO-FETCH: User table se data match karke fill karna
        if self.user and not self.university_record:
            try:
                record = UniversityID.objects.get(university_id=self.user.university_id, role='worker')
                self.university_record = record
                self.worker_id = record.university_id
                self.name = record.full_name
                record.is_used = True # ID ko used mark karna
                record.save()
            except UniversityID.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.worker_id})"

# -------------------------
# OPERATIONAL TABLES
# -------------------------

class Attendance(models.Model):
    STATUS_CHOICES = [('Present', 'present'), ('Absent', 'absent'), ('Leave', 'leave')]
    
    # FIXED: Linked to UniversityID so unregistered workers can have attendance
    worker_master = models.ForeignKey(UniversityID, on_delete=models.CASCADE)
    warden = models.ForeignKey(Warden, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('worker_master', 'date') 

from django.db import models
from django.utils import timezone

class Inventory(models.Model):
    item_id = models.CharField(max_length=20, unique=True) 
    item_name = models.CharField(max_length=100)
    current_stock = models.FloatField(default=0.0)
    required_stock = models.FloatField(default=0.0)
    unit = models.CharField(max_length=10, default='kg')
    is_delivered = models.BooleanField(default=False) 

    @property
    def get_status(self):
        """Calculates status based on current vs required stock"""
        if self.current_stock <= (self.required_stock * 0.2):
            return "Critical"
        elif self.current_stock <= (self.required_stock * 0.5):
            return "Low"
        else:
            return "Good"

    # --- Naya Logic: Auto-track Consumption ---
    def save(self, *args, **kwargs):
        if self.pk:  # Agar item pehle se database mein hai (Update ho raha hai)
            # Database se purani value uthao
            old_instance = Inventory.objects.get(pk=self.pk)
            old_stock = old_instance.current_stock
            
            # Agar Warden ne stock kam kiya hai, matlab consumption hua hai
            if old_stock > self.current_stock:
                consumption = old_stock - self.current_stock
                # DailyUsage table mein entry create karo
                # Note: DailyUsage model niche define hona chahiye
                DailyUsage.objects.create(
                    item=self,
                    quantity_used=consumption,
                    date=timezone.now().date()
                )
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} ({self.get_status})"

class DailyUsage(models.Model):
    item = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='usages')
    quantity_used = models.FloatField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.item.item_name} - {self.quantity_used} used on {self.date}"
    




class DeliveryOrder(models.Model):
    item = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    qty_delivered = models.FloatField()
    otp = models.CharField(max_length=6)
    status = models.CharField(max_length=20, default='DISPATCHED')
    # YEH LINE ADD KAREIN 👇
    ai_remark = models.CharField(max_length=255, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.item.item_name}"



    
        
class LeaveRequest(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True, blank=True)
    worker_master = models.ForeignKey(UniversityID, on_delete=models.SET_NULL, null=True, blank=True)
    warden = models.ForeignKey(Warden, on_delete=models.CASCADE)
    is_warden_request = models.BooleanField(default=False)
    leave_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reason = models.TextField(null=True, blank=True)
    attachment = models.FileField(upload_to='leave_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def display_worker_name(self):
        if self.is_warden_request:
            return "Self (Warden)"
        if self.worker:
            return self.worker.name or self.worker.worker_id
        if self.worker_master:
            return self.worker_master.full_name or self.worker_master.university_id
        return "Unknown Worker"

#sneha ka edit (Notification)
class Notification(models.Model):
    TYPE_CHOICES = (
        ('alert', 'Alert / Absent'),
        ('leave', 'Leave Status'),
        ('user', 'New User Registration'),
        ('finance', 'Salary / Finance'),
    )
    # 👈 Yeh field add karein taaki worker ko apna notification mile
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    message = models.CharField(max_length=255)
    noti_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.recipient.username if self.recipient else 'All'}: {self.message}"

class GeneratedReport(models.Model):
    REPORT_TYPE_CHOICES = (
        ('summary_pdf', 'Summary PDF'),
        ('worker_excel', 'Worker Excel'),
    )

    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    file = models.FileField(upload_to='saved_reports/')
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.report_type})"
