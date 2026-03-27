#views.py
# Shree1/views.py
from django.db.models import Q 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime 
from django.urls import reverse 
from accounts.models import User, UniversityID, Worker, Warden, Supplier, Attendance, Inventory, LeaveRequest





def welcome_role(request):
    return render(request, 'Shree1/home.html')

def login_selection(request):
    return render(request, 'Shree1/login_role.html')

def role_selection(request):
    return render(request, 'Shree1/signup_role.html')

# --- Dynamic Admin Views ---

@login_required
def admin_dashboard(request):
    context = {
        'warden_count': Warden.objects.count(),
        'worker_count': Worker.objects.count(),
        'supplier_count': Supplier.objects.count(),
        'admin_name': request.user.username,
    }
    return render(request, 'Shree1/dashboardAdmin.html', context)

@login_required
def admin_user_management(request):
    wardens = Warden.objects.all()
    workers = Worker.objects.all()
    auth_ids = UniversityID.objects.all().order_by('-id')
    return render(request, 'Shree1/admin_user_management.html', {
        'wardens': wardens,
        'workers': workers,
        'auth_ids': auth_ids
    })

@login_required
def admin_attendance(request):
    # YAHAN CHANGE KIYA HAI: Ab Admin seedha UniversityID table se workers uthayega!
    master_workers = UniversityID.objects.filter(role='worker')
    today = timezone.now().date()
    today_str = today.strftime('%Y-%m-%d')

    # --- 1. DETERMINE THE DATE WE ARE LOOKING AT ---
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            current_date_obj = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            current_date_str = selected_date_str
        except ValueError:
            current_date_obj = today
            current_date_str = today_str
    else:
        current_date_obj = today
        current_date_str = today_str

    # --- 2. HANDLE POST (ADMIN SAVING ATTENDANCE) ---
    if request.method == "POST":
        save_date = request.POST.get('save_date') or current_date_str
        
        for master in master_workers:
            # Ab hum master.university_id se check kar rahe hain
            status = request.POST.get(f'status_{master.university_id}')
            if status:
                admin_warden = Warden.objects.first()
                try:
                    Attendance.objects.update_or_create(
                        worker_master=master,
                        date=current_date_obj,
                        defaults={'status': status.strip(), 'warden': admin_warden}
                    )
                except Exception:
                    Attendance.objects.update_or_create(
                        worker_master=master,
                        date=save_date,
                        defaults={'status': status.strip(), 'warden': admin_warden}
                    )

        messages.success(request, f"Attendance for {save_date} updated.")
        return redirect(f"{reverse('admin_attendance')}?date={save_date}")


    # --- 3. FETCH ATTENDANCE (100% MATCH WITH WARDEN) ---
    worker_data_list = []
    present_count = 0
    absent_count = 0

    attendances = list(Attendance.objects.filter(date=current_date_obj))
    if not attendances:
        attendances = list(Attendance.objects.filter(date=current_date_str))

    for master in master_workers:
        db_status = ""
        warden_name = "N/A"
        warden_id = "N/A"
        
        master_id_clean = str(master.university_id).strip().lower()

        for att in attendances:
            if att.worker_master:
                att_uid_clean = str(att.worker_master.university_id).strip().lower()
                
                # Agar ID match ho gayi
                if master_id_clean == att_uid_clean:
                    db_status = str(att.status).strip()
                    if att.warden:
                        warden_name = getattr(att.warden, 'name', 'N/A')
                        warden_id = getattr(att.warden, 'warden_id', 'N/A')
                    break 

        if db_status.lower() == 'present':
            present_count += 1
        elif db_status.lower() == 'absent':
            absent_count += 1

        worker_data_list.append({
            'worker_id': master.university_id, # UI par dikhane ke liye
            'name': master.full_name,          # UI par dikhane ke liye
            'status': db_status,
            'warden_name': warden_name,
            'warden_id': warden_id,
        })

    return render(request, 'Shree1/admin_attendance.html', {
        'workers': worker_data_list,  
        'today_str': today_str,               
        'current_date_str': current_date_str, 
        'present_count': present_count,
        'absent_count': absent_count,
    })
@login_required
def admin_inventory(request):
    items = Inventory.objects.all()
    total = items.count()
    critical = sum(1 for i in items if i.current_stock < (i.required_stock * 0.2))
    low = sum(1 for i in items if i.current_stock < (i.required_stock * 0.5) and i.current_stock >= (i.required_stock * 0.2))
    
    return render(request, 'Shree1/admin_inventory.html', {
        'items': items,
        'total_items': total,
        'critical_count': critical,
        'low_count': low,
        'good_count': total - (critical + low)
    })

@login_required
def admin_leave_Management(request):
    if request.method == "POST":
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')
        leave_req = get_object_or_404(LeaveRequest, id=leave_id)
        leave_req.status = action
        leave_req.save()
        messages.success(request, f"Leave request {action} for {leave_req.worker.name}.")
        return redirect('admin_leave_Management')

    pending = LeaveRequest.objects.filter(status='Pending')
    return render(request, 'Shree1/admin_leave_Management.html', {'pending': pending})
@login_required
def admin_profile(request):

    if 'profile' not in request.session:
        request.session['profile'] = {
            'username': 'Shree',
            'email': 'slzmdl@gmail.com',
            'phone': '9876543210',
        }

    profile = request.session['profile']

    if request.method == "POST":
        email = request.POST.get('email')
        phone = request.POST.get('phone').strip()

        if not phone.isdigit():
            messages.error(request, "Phone must contain only digits.")

        elif len(phone) != 10:
            messages.error(request, "Phone must be exactly 10 digits.")

        elif phone[0] == '0':
            messages.error(request, "Phone cannot start with 0.")

        else:
            profile['email'] = email
            profile['phone'] = phone
            request.session['profile'] = profile

            messages.success(request, "Profile updated successfully!")
            return redirect('admin_profile')

    return render(request, 'Shree1/admin_profile.html', profile)

