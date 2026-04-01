#views.py
# Shree1/views.py
from django.db.models import Q 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime 
from django.urls import reverse 
from accounts.models import User, UniversityID, Worker, Warden, Supplier, Attendance, Inventory, LeaveRequest , Notification





def welcome_role(request):
    return render(request, 'Shree1/home.html')

def login_selection(request):
    return render(request, 'Shree1/login_role.html')

def role_selection(request):
    return render(request, 'Shree1/signup_role.html')

# --- Dynamic Admin Views ---

@login_required
def admin_dashboard(request):
    # Ab hum UniversityID ko count kar rahe hain. 
    # Jaise hi aap naya add/delete karengi, yeh number turant badlega!
    warden_count = UniversityID.objects.filter(role__iexact='warden').count()
    worker_count = UniversityID.objects.filter(role__iexact='worker').count()
    
    # 2. Aaj ki attendance
    today = timezone.now().date()
    present_workers = Attendance.objects.filter(date=today, status__iexact='Present').count()
    absent_workers = Attendance.objects.filter(date=today, status__iexact='Absent').count()
    
    # 3. Latest Notifications
    recent_notifications = Notification.objects.order_by('-created_at')[:5]
    
    context = {
        'admin_name': request.user.username if request.user.is_authenticated else 'Admin',
        'warden_count': warden_count,
        'worker_count': worker_count, 
        'present_workers': present_workers,
        'absent_workers': absent_workers,
        'recent_notifications': recent_notifications,
    }
    
    return render(request, 'Shree1/dashboardAdmin.html', context)

def admin_user_management(request):  #sneha ka new update
    
    unused_ids = UniversityID.objects.filter(is_used=False)
    
    wardens = UniversityID.objects.filter(is_used=True, role__iexact='warden')
    
    workers = UniversityID.objects.filter(is_used=True, role__iexact='worker')
    
    # Context mein in teeno ko alag-alag HTML mein bhejein
    context = {
        'unused_ids': unused_ids,
        'wardens': wardens,
        'workers': workers,
    }
    
    return render(request, 'Shree1/admin_user_management.html', context)
@login_required #sneha edit
def admin_attendance(request):
    # Admin seedha UniversityID table se workers uthayega
    master_workers = UniversityID.objects.filter(role='worker')
    today = timezone.now().date()
    today_str = today.strftime('%Y-%m-%d')

    # --- 1. DETERMINE THE DATE ---
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

    # --- 2. HANDLE POST (ADMIN SAVING/UPDATING ATTENDANCE) ---
    if request.method == "POST":
        save_date = request.POST.get('save_date') or current_date_str
        
        for master in master_workers:
            status = request.POST.get(f'status_{master.university_id}')
            if status:
                admin_warden = Warden.objects.first()
                try:
                    # Attendance update ya create karein
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

                # --- 🔔 ADMIN NOTIFICATION LOGIC (ALWAYS NOTIFY) ---
                # Admin jab bhi update karega (Present/Absent), worker ko noti jayega
                worker_user = User.objects.filter(university_id=master.university_id).first()
                
                if worker_user:
                    # Absent ke liye red alert, baki ke liye blue info icon
                    noti_type_val = 'alert' if status.strip().lower() == 'absent' else 'user'
                    
                    Notification.objects.create(
                        recipient=worker_user,
                        message=f"Admin updated your attendance to {status} for {save_date}.",
                        noti_type=noti_type_val
                    )

        messages.success(request, f"Attendance for {save_date} updated and workers notified.")
        return redirect(f"{reverse('admin_attendance')}?date={save_date}")


    # --- 3. FETCH ATTENDANCE DATA ---
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
            'worker_id': master.university_id,
            'name': master.full_name,
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
    
    # --- YAHAN SE NAYA LOGIC SHURU (Button clicks handle karne ke liye) ---
    if request.method == "POST":
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action') # Yeh HTML se "Approved" ya "Rejected" aayega

        if leave_id and action:
            # 1. Leave Request ko database mein update karo
            leave_req = get_object_or_404(LeaveRequest, id=leave_id)
            leave_req.status = action
            leave_req.save()

            # 2. Dynamic Notification Create karo!
            # Hum recipient mein 'leave_req.worker.user' pass karenge 
            # taaki worker ko notification mile.
            
            if action == 'Approved':
                Notification.objects.create(
                    recipient=leave_req.worker.user, # Specific worker ko jayega
                    message=f"Your leave request from {leave_req.start_date} has been Approved.",
                    noti_type='leave' # Yellow icon
                )
            else:
                Notification.objects.create(
                    recipient=leave_req.worker.user, # Specific worker ko jayega
                    message=f"Your leave request from {leave_req.start_date} has been Rejected.",
                    noti_type='alert' # Red icon
                )

            # 3. Success message dikhao aur page refresh karo
            messages.success(request, f"Leave request for {leave_req.worker.name} {action.lower()} successfully!")
            return redirect('admin_leave_Management')
    # --- YAHAN NAYA LOGIC KHATAM ---


    # --- PURANA LOGIC (Data dikhane ke liye) ---
    pending_requests = LeaveRequest.objects.filter(status='Pending')
    leave_history = LeaveRequest.objects.exclude(status='Pending').order_by('-created_at') # latest pehle
    
    context = {
        'pending': pending_requests,
        'leave_history': leave_history, 
    }
    return render(request, 'Shree1/admin_leave_Management.html', context)

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

@login_required
def add_university_id(request): #sneha edit
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        uni_id = request.POST.get('uni_id')
        role = request.POST.get('role')

        # Database mein naya ID save karna
        UniversityID.objects.create(
            full_name=full_name, 
            university_id=uni_id, 
            role=role
        )

        # ---> NAYA NOTIFICATION LOGIC <---
        Notification.objects.create(
            message=f"New {role} authorized: {full_name}",
            noti_type='user' # Blue icon aayega (user registration ke liye)
        )

        messages.success(request, "New ID Authorized successfully!")
        return redirect('admin_user_management')
    
@login_required
def delete_uni_id(request, id): # sneha edit
    # 1. Jo ID delete karni hai use find karein
    obj = get_object_or_404(UniversityID, id=id)
    name = obj.full_name
    role = obj.role
    
    # 2. Database se delete karein
    obj.delete()

    # 3. ---> DYNAMIC NOTIFICATION <---
    Notification.objects.create(
        message=f"{role.capitalize()} ID revoked/deleted: {name}",
        noti_type='alert' # Red alert icon aayega kyunki kuch delete hua hai
    )

    messages.success(request, f"ID for {name} deleted successfully!")
    return redirect('admin_user_management')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Inventory, DailyUsage 
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import Inventory, DailyUsage

@login_required
def admin_inventory(request):
    if request.method == "POST":
        # Form se data nikalna
        name = request.POST.get('item_name')
        current = request.POST.get('current_stock')
        required = request.POST.get('required_stock')
        unit = request.POST.get('unit')

        # Database mein save karna
        Inventory.objects.create(
            item_name=name,
            current_stock=current,
            required_stock=required,
            unit=unit
        )
        messages.success(request, f"{name} added successfully!")
        return redirect('admin_inventory')

    # Baki ka purana logic (GET request ke liye)
    items = Inventory.objects.all()
    critical_count = sum(1 for i in items if i.current_stock == 0 or (i.required_stock > 0 and i.current_stock <= i.required_stock * 0.2))
    low_count = sum(1 for i in items if i.required_stock > 0 and i.current_stock <= i.required_stock * 0.5 and not (i.current_stock == 0 or i.current_stock <= i.required_stock * 0.2))
    
    recent_usage = DailyUsage.objects.select_related('item').order_by('-date', '-id')[:10]

    context = {
        'items': items,
        'low_count': low_count,
        'critical_count': critical_count,
        'status': "Attention Needed" if critical_count > 0 else "Healthy",
        'recent_usage': recent_usage,
    }
    return render(request, 'Shree1/admin_inventory.html', context)




# Add New Item Logic (Dynamic Button ke liye)
@login_required
def add_inventory_item(request):
    # Abhi ke liye hum ise Django Admin par redirect kar sakte hain
    # Ya aap yahan apna custom form handle kar sakte hain
    return redirect('/admin/accounts/inventory/add/')