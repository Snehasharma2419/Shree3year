from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UniversityID, Worker, Warden, Supplier, Attendance, Inventory, LeaveRequest, DeliveryOrder
from .models import Notification




# 1. CUSTOM USER ADMIN (Registration logic fix)
class CustomUserAdmin(UserAdmin):
    # 'Add User' screen par extra fields dikhane ke liye
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('university_id', 'role')}),
    )
    
    # 'Change User' (Edit) screen par extra fields dikhane ke liye
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('university_id', 'role', 'phone')}),
    )
    
    list_display = ['username', 'university_id', 'role', 'is_staff']

# User ko sirf EK BAAR register karein CustomUserAdmin ke saath
admin.site.register(User, CustomUserAdmin)

# 2. UNIVERSITY ID & PROFILES
admin.site.register(UniversityID)
admin.site.register(Worker)
admin.site.register(Supplier)

class WardenAdmin(admin.ModelAdmin):
    list_display = ('warden_id', 'name', 'phone_number', 'leave_balance')

admin.site.register(Warden, WardenAdmin)


class AttendanceAdmin(admin.ModelAdmin):
    
    @admin.display(description="Status")  
    def get_status(self, obj):
        return obj.status
    
    list_display = ('worker_master', 'date', 'get_status', 'warden') # Columns to show
    list_filter = ('date', 'status', 'warden') # Sidebar filters
    search_fields = ('worker_master__full_name', 'worker_master__university_id') # Search bar

admin.site.register(Attendance, AttendanceAdmin)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    # Admin panel par jo columns aap dekhna chahte hain
    list_display = ('item_id', 'item_name', 'current_stock', 'required_stock', 'unit')
    # Search karne ke liye fields
    search_fields = ('item_id', 'item_name')



@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    # Admin panel ki table mein kaunse columns dikhen
    list_display = ('worker', 'leave_type', 'start_date', 'end_date', 'status', 'warden')
    
    # Side mein filter lagane ke liye
    list_filter = ('status', 'leave_type', 'start_date')
    
    # Search bar ke liye
    search_fields = ('worker__name', 'warden__name')

    # Status badalne ke liye custom actions
    actions = ['approve_leave', 'reject_leave']

    def approve_leave(self, request, queryset):
        queryset.update(status='Approved')
    approve_leave.short_description = "Mark selected requests as Approved"

    def reject_leave(self, request, queryset):
        queryset.update(status='Rejected')
    reject_leave.short_description = "Mark selected requests as Rejected"

admin.site.register(Notification) #sneha edit

# OTP aur baki details table format mein dekhne ke liye
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'otp', 'status', 'created_at') 
    # Jo fields aap dekhna chahte hain unhe yahan likhein

admin.site.register(DeliveryOrder, ShipmentAdmin)

