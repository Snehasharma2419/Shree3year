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
    university_record = models.OneToOneField(UniversityID, on_delete=models.CASCADE, null=True, limit_choices_to={'role': 'worker'})
    worker_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    # The Admin field stays nullable so they can signup themselves
    admin_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_workers')
    
    # Logic improvements
    is_approved = models.BooleanField(default=False)
    leave_balance = models.IntegerField(default=15)
    
    def __str__(self):
        return f"{self.name} ({self.worker_id})"



# -------------------------
# OPERATIONAL TABLES
# -------------------------

class Attendance(models.Model):
    STATUS_CHOICES = [('Present', 'Present'), ('Absent', 'Absent'), ('Leave', 'Leave')]
    
    # FIXED: Linked to UniversityID so unregistered workers can have attendance
    worker_master = models.ForeignKey(UniversityID, on_delete=models.CASCADE)
    warden = models.ForeignKey(Warden, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('worker_master', 'date') 

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
        # Agar current stock required stock ke 20% ya usse kam hai
        if self.current_stock <= (self.required_stock * 0.2):
            return "Critical"
        # Agar current stock required stock ke 50% ya usse kam hai
        elif self.current_stock <= (self.required_stock * 0.5):
            return "Low"
        else:
            return "Good"

    def __str__(self):
        return f"{self.item_name} ({self.get_status})"
    

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
    warden = models.ForeignKey(Warden, on_delete=models.CASCADE)
    is_warden_request = models.BooleanField(default=False)
    leave_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    