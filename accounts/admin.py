from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, UniversityID, Worker, Warden, Supplier, 
    Attendance, Inventory, LeaveRequest, DeliveryOrder, 
    DailyUsage, Notification, GeneratedReport
)

# 1. CUSTOM USER ADMIN
class CustomUserAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('university_id', 'role')}),
    )
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('university_id', 'role', 'phone')}),
    )
    list_display = ['username', 'university_id', 'role', 'is_staff']

admin.site.register(User, CustomUserAdmin)

# 2. SIMPLE REGISTRATIONS
admin.site.register(UniversityID)
admin.site.register(Worker)
admin.site.register(Supplier)
admin.site.register(Notification)

# 3. WARDEN ADMIN
class WardenAdmin(admin.ModelAdmin):
    list_display = ('warden_id', 'name', 'phone_number', 'leave_balance')

admin.site.register(Warden, WardenAdmin)

# 4. ATTENDANCE ADMIN
class AttendanceAdmin(admin.ModelAdmin):
    @admin.display(description="Status")  
    def get_status(self, obj):
        return obj.status
    
    list_display = ('worker_master', 'date', 'get_status', 'warden')
    list_filter = ('date', 'status', 'warden')
    search_fields = ('worker_master__full_name', 'worker_master__university_id')

admin.site.register(Attendance, AttendanceAdmin)

# 5. LEAVE REQUEST ADMIN
@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('worker', 'leave_type', 'start_date', 'end_date', 'status', 'warden')
    list_filter = ('status', 'leave_type', 'start_date')
    search_fields = ('worker__name', 'warden__name')
    actions = ['approve_leave', 'reject_leave']

    def approve_leave(self, request, queryset):
        queryset.update(status='Approved')
    
    def reject_leave(self, request, queryset):
        queryset.update(status='Rejected')

# 6. SHIPMENT / DELIVERY ORDER
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'otp', 'status', 'created_at')

admin.site.register(DeliveryOrder, ShipmentAdmin)

# 7. INVENTORY & DAILY USAGE (The AI Logic Part)
class DailyUsageInline(admin.TabularInline):
    model = DailyUsage
    extra = 1
    fields = ('quantity_used', 'date')
    readonly_fields = ('date',)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'item_name', 'current_stock', 'required_stock', 'unit', 'stock_status')
    search_fields = ('item_id', 'item_name')
    inlines = [DailyUsageInline]

    def stock_status(self, obj):
        if obj.current_stock <= (obj.required_stock * 0.2):
            return "⚠️ Critical (Low Stock)"
        elif obj.current_stock <= (obj.required_stock * 0.5):
            return "🟡 Low"
        return "✅ Good"
    stock_status.short_description = 'AI Stock Alert'

@admin.register(DailyUsage)
class DailyUsageAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity_used', 'date')
    list_filter = ('date', 'item')
    search_fields = ('item__item_name',)


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'generated_by', 'created_at', 'file')
    list_filter = ('report_type', 'created_at')
    search_fields = ('title', 'generated_by__username')
    readonly_fields = ('created_at',)
