from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .models import User, UniversityID, Worker, Warden, Supplier, Attendance, Inventory, LeaveRequest, Notification, GeneratedReport, DailyUsage
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from django.db.models import F
from datetime import datetime, date
from django.db import transaction, IntegrityError
from django.contrib import messages
import re
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.urls import reverse
     

# -------------------------------
# 1. NAVIGATION PAGES
# -------------------------------
def welcome_role(request):
    return render(request, 'Shree1/home.html')

def login_selection(request):
    return render(request, 'Shree1/login_role.html')

def role_selection(request):
    return render(request, 'Shree1/signup_role.html')


# -------------------------------
# 2. PASSWORD CONSTRAINTS (HELPER)
# -------------------------------
def validate_password(password, confirm_password):
    if password != confirm_password:
        return "Passwords do not match."

    if len(password) < 5:
        return "Password must be at least 5 characters long."

    return None

# -------------------------------
# 3. SIGNUP LOGIC (UPDATED)
# -------------------------------

def worker_signup_view(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Security fields capture karein
        security_question = request.POST.get('security_question')
        security_answer = request.POST.get('security_answer')

        # 1. Password Validation
        error = validate_password(password, confirm_password)
        if error:
            messages.error(request, error)
            return render(request, 'Shree1/signupWorker.html')

        # 2. UniversityID Check (Check if authorized and unused)
        record = UniversityID.objects.filter(
            university_id=user_id,
            role='worker',
            is_used=False
        ).first()

        if not record or record.full_name != full_name:
            messages.error(request, "Access Denied: Invalid credentials or name mismatch.")
            return render(request, 'Shree1/signupWorker.html')

        # 3. Create the central User
        new_user = User.objects.create_user(
            username=user_id,
            university_id=user_id,
            first_name=full_name,
            password=password,
            role='worker'
        )
        
        # ✅ YAHAN SAVE HOGA SECURITY DATA (Corrected Indentation)
        new_user.security_question = security_question
        new_user.security_answer = security_answer
        new_user.save()

        # 4. !!! UPDATED: Link to EXISTING Worker Profile !!!
        try:
            worker_profile = Worker.objects.get(worker_id=user_id)
            worker_profile.user = new_user
            worker_profile.save()
        except Worker.DoesNotExist:
            # Fallback agar Admin ne pre-fill nahi kiya tha
            Worker.objects.create(user=new_user, worker_id=user_id, name=full_name)

        # 5. Mark record as used
        record.is_used = True
        record.save()

        #6. admin ko noti jaega
        admin_user = User.objects.filter(role='admin').first() or User.objects.filter(is_superuser=True).first()
        if admin_user:
            Notification.objects.create(
                recipient=admin_user,
                 message=f"New User Registered: {full_name} ({user_id}) as {new_user.role}.",
                noti_type='user'
        )

        # 7. Login the user
        login(request, new_user)
        messages.success(request, f"Welcome {full_name}!")
        return redirect('worker_dashboard')
        
        

    return render(request, 'Shree1/signupWorker.html')


def warden_signup_view(request):
    if request.method == "POST":
        # 1. Variables capture karein
        u_id = request.POST.get('user_id', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Security fields capture karein
        security_question = request.POST.get('security_question')
        security_answer = request.POST.get('security_answer')

        # 2. Password Validation
        error = validate_password(password, confirm_password)
        if error:
            messages.error(request, error)
            return render(request, 'Shree1/signupWarden.html')

        # 3. UniversityID Check (Check if authorized and not yet used)
        record = UniversityID.objects.filter(
            university_id=u_id,
            role='warden',
            is_used=False
        ).first()

        if not record:
            messages.error(request, "Invalid ID or Account already exists.")
            return render(request, 'Shree1/signupWarden.html')

        # 4. Central User Create Karein
        new_user = User.objects.create_user(
            username=u_id,
            university_id=u_id,
            first_name=full_name,
            password=password,
            role='warden'
        )
        
        # ✅ YAHAN SAVE HOGA SECURITY DATA (Corrected Indentation)
        new_user.security_question = security_question
        new_user.security_answer = security_answer
        new_user.save()

        # 5. !!! CRITICAL CHANGE: Link to EXISTING Profile !!!
        # Naya create karne ke bajaye existing profile ko update karein
        try:
            warden_profile = Warden.objects.get(warden_id=u_id)
            warden_profile.user = new_user  # Auth user link kar diya
            warden_profile.save()
        except Warden.DoesNotExist:
            # Backup: Agar Admin ne profile nahi banayi thi, toh yahan bana dein
            Warden.objects.create(user=new_user, warden_id=u_id, name=full_name)

        # 6. Mark ID as used
        record.is_used = True
        record.save()

          #admin ko noti jaega aignup k tym
            # Signup success hone ke baad aur is_used = True karne ke baad:
        admin_user = User.objects.filter(Q(role='admin') | Q(is_superuser=True)).first()
        
        if admin_user:
            Notification.objects.create(
                recipient=admin_user,
                message=f"New User Registered: {full_name} ({u_id}) as Warden.",
                noti_type='user'
            )

        # 7. Login and Redirect
        login(request, new_user)
        messages.success(request, f"Welcome Warden {full_name}!")
        return redirect('warden_dashboard')

    return render(request, 'Shree1/signupWarden.html')

# -------------------------------
# 5. ADMIN ACTIONS (MANAGEMENT)
# -------------------------------

@login_required
def add_university_id(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        uni_id = request.POST.get('uni_id')
        role = request.POST.get('role')
        UniversityID.objects.create(university_id=uni_id, full_name=full_name, role=role)
        messages.success(request, f"ID {uni_id} authorized.")
    return redirect('admin_user_management')

@login_required
def delete_uni_id(request, pk):
    record = get_object_or_404(UniversityID, id=pk)
    record.delete()
    messages.success(request, "Record removed.")
    return redirect('admin_user_management')

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    UniversityID.objects.filter(university_id=user.university_id).update(is_used=False)
    user.delete()
    messages.success(request, "User deleted.")
    return redirect('admin_user_management')

# -------------------------------
# 4. DASHBOARDS & FEATURES
# -------------------------------


@login_required #sneha edit
def attendance_view(request):
    try:
        warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        return redirect('welcome_role')

    master_list = UniversityID.objects.filter(role='worker')
    
    # --- 1. DATE HANDLING ---
    today = timezone.now().date()
    today_str = today.strftime('%Y-%m-%d')

    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            current_date_obj = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            if current_date_obj > today:
                current_date_obj = today
            current_date_str = current_date_obj.strftime('%Y-%m-%d')
        except ValueError:
            current_date_obj = today
            current_date_str = today_str
    else:
        current_date_obj = today
        current_date_str = today_str

    # --- 2. LOCKING LOGIC ---
    existing_attendance = Attendance.objects.filter(date=current_date_obj)
    is_locked = existing_attendance.exists()

    # --- 3. SAVE ATTENDANCE (POST REQUEST) ---
    if request.method == "POST":
        if is_locked:
            messages.error(request, f"Attendance for {current_date_str} is already locked!")
            return redirect(f"{reverse('attendance')}?date={current_date_str}")

        for person in master_list:
            status = request.POST.get(f'status_{person.university_id}')
            if status:
                # Attendance Record Create karein
                Attendance.objects.create(
                    worker_master=person,
                    date=current_date_obj,
                    status=status.strip(),
                    warden=warden
                )

                # --- 🔔 SNEHA NOTIFICATION LOGIC (ONLY FOR ABSENT) ---
                if status.strip().lower() == 'absent':
                    # Master record se User dhoondo taaki recipient mil sake
                    worker_user = User.objects.filter(university_id=person.university_id).first()
                    
                    if worker_user:
                        Notification.objects.create(
                            recipient=worker_user,
                            message=f"Warden marked you ABSENT for {current_date_str}.",
                            noti_type='alert' # Red alert badge
                        )

        messages.success(request, f"Attendance for {current_date_str} saved. Absent workers notified.")
        return redirect(f"{reverse('attendance')}?date={current_date_str}")

    # --- 4. PREPARE DATA FOR HTML ---
    worker_data_list = []
    for person in master_list:
        status = 'Present' # Default UI
        
        if is_locked:
            att_record = existing_attendance.filter(worker_master=person).first()
            if att_record:
                status = att_record.status

        worker_data_list.append({
            'worker_id': person.university_id,
            'name': person.full_name,
            'status': status
        })

    # --- 5. SEND CONTEXT ---
    context = {
        'workers': worker_data_list,
        'current_date_str': current_date_str,
        'today_str': today_str,
        'is_locked': is_locked,
        'warden': warden,
    }

    return render(request, 'Shree1/warden_attendance.html', context)


@login_required
@login_required
def worker_dashboard(request):


    if not request.user.is_authenticated:
        return redirect('worker_login')

    try:
        # 1. Profile aur Master Record Linkage
        worker_profile = Worker.objects.get(user=request.user)
        master_record = UniversityID.objects.get(university_id=worker_profile.worker_id)

    except (Worker.DoesNotExist, UniversityID.DoesNotExist):
        return redirect('welcome_role')

    # 2. Attendance Metrics
    # Pura record fetch karna summary ke liye
    all_attendance = Attendance.objects.filter(worker_master=master_record)
    
    # Latest 5 records table mein dikhane ke liye
    latest_attendance = all_attendance.order_by('-date')[:5]

    present_days = all_attendance.filter(status='Present').count()
    total_days = all_attendance.count()

    # 3. Dynamic Notifications Logic (SNEHA EDIT)
    # 👈 Yahan hum Notification model se worker ke specific messages nikal rahe hain
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:5] # Latest 5 notifications

    # Unread notifications ka count (Badge ke liye)
    notifications_count = Notification.objects.filter(
        recipient=request.user, 
        is_read=False
    ).count()

    # 4. Leave Balance
    leave_balance = getattr(worker_profile, 'leave_balance', 0)

    context = {
        # Profile Data
        'worker': worker_profile,
        'master': master_record,
        'full_name': master_record.full_name,
        
        # Attendance Data
        'attendance_list': latest_attendance,
        'present_days': present_days,
        'total_days': total_days,
        
        # Notifications & Real-time Data
        'notifications': notifications,       # Dashboard loop ke liye
        'notifications_count': notifications_count, # Icon par red dot dikhane ke liye
        'leave_balance': leave_balance,
        'salary': 15000, # Future logic: present_days * per_day_salary
    }

    return render(request, 'Shree1/dashboardWorker.html', context)


from django.db.models import F
from django.contrib import messages

# -------------------------------
# 3. KUTIR'S CENTRAL DASHBOARD
# -------------------------------

from django.db.models import F
from .models import Inventory, DeliveryOrder # DeliveryOrder model zaroori hai

@login_required
@never_cache
def supplier_dashboard(request):

    if not request.user.is_authenticated:
        return redirect('suplier_login')


    # 1. Wo items nikalna jinka stock kam hai (Deficit calculation ke saath)
    # Hum annotation use karenge deficit calculate karne ke liye
    critical_items = Inventory.objects.filter(
        current_stock__lte=F('required_stock') * 0.2
    ).annotate(
        deficit=F('required_stock') - F('current_stock')
    )

    pending_items = Inventory.objects.filter(
        current_stock__lt=F('required_stock')
    ).annotate(
        deficit=F('required_stock') - F('current_stock')
    )

    # 2. Wo shipments jo raste mein hain (At Gate)
    active_shipments = DeliveryOrder.objects.filter(
        status='DISPATCHED'
    ).select_related('item')

    # 3. Stats calculate karna
    total_items_count = Inventory.objects.count()
    
    context = {
        'pending_items': pending_items,
        'critical_items': critical_items,
        'active_shipments': active_shipments,
        'total_items_count': total_items_count,
    }
    
    return render(request, 'Shree1/dashboardSupplier.html', context)


import random
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Inventory, DeliveryOrder
import random
from django.contrib import messages
from django.shortcuts import redirect

    




@login_required
def worker_profile(request):
    try:
        worker = Worker.objects.get(user=request.user)
    except Worker.DoesNotExist:
        return redirect('welcome_role')

    # -------- SAVE DATA --------
    if request.method == "POST":
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        
        if not re.match(r'^[1-9][0-9]{9}$', phone):
            messages.error(request, "Phone number must be 10 digits and cannot start with 0.")
            return redirect('worker_profile')

        # update email in User model
        request.user.email = email
        request.user.phone = phone
        request.user.save()

        # update phone in Worker model
        worker.email = email
        worker.phone_number = phone
        worker.save()


        messages.success(request, "Profile updated successfully!")
        return redirect('worker_profile')

    # -------- DISPLAY DATA --------
    context = {
        # 🔝 RIGHT TOP HEADER
         "display_name": worker.name,   # 👈 RIYA (DB se)
    "display_role": "Worker",

        # 📝 PROFILE FORM
        "full_name": worker.name,
        "employee_id": worker.worker_id,
        "email": request.user.email,
        "phone": worker.phone_number,
        "joining_date": request.user.date_joined.strftime("%d %B %Y"),

    }

    return render(request, "Shree1/workerProfile.html", context)



# -------------------------------
# 4. KUTIR'S PROFILE (READ ONLY OR SIMPLE UPDATE)
# -------------------------------
@login_required
def supplier_profile(request):
    # Hum seedha login user ka data uthayenge
    context = {
        "display_name": "Kutir Supplies",
        "display_role": "Official Hostel Supplier",
        "email":"kutir@gmail.com",
        "phone": "9876543210", # Static ya DB se
        "address": "Main Market, University Area"
    }
    return render(request, 'Shree1/supplier_profile.html', context)


from django.db.models import Q


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Inventory, Warden
from django.db.models import F



@login_required
def inventory_view(request):
    # Warden ki info nikalna
    try:
        # User model se linked warden profile fetch karna
        warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        warden = None

    # Hamesha pure database se stats calculate karein (Cards ke liye)
    # Taaki search karne par bhi total inventory status sahi dikhe
    all_inventory = Inventory.objects.all()
    total_items = all_inventory.count()
    
    # Critical logic: Stock <= 20% of Required
    critical_items = all_inventory.filter(current_stock__lte=F('required_stock') * 0.2)
    critical_count = critical_items.count()
    
    # Low logic: 20% < Stock <= 50%
    low_count = all_inventory.filter(
        current_stock__lte=F('required_stock') * 0.5,
        current_stock__gt=F('required_stock') * 0.2
    ).count()
    
    good_count = total_items - critical_count - low_count

    # Search Logic (Sirf table ke items filter honge)
    search_query = request.GET.get('search', '')
    if search_query:
        items = all_inventory.filter(
            Q(item_name__icontains=search_query) | 
            Q(item_id__icontains=search_query)
        )
    else:
        items = all_inventory

    context = {
        'items': items,
        'warden': warden,
        'total_items': total_items,
        'critical_count': critical_count,
        'has_critical_stock': critical_count > 0,
        'low_count': low_count,
        'good_count': good_count,
        'search_query': search_query
    }
    return render(request, 'Shree1/warden_inventory.html', context)


from django.shortcuts import redirect
from django.contrib import messages
from .models import Inventory

@login_required
def update_inventory_stock(request):
    if request.method == "POST":
        updated = False
        
        # Sirf wahi fields nikalna jo "qty_" se shuru ho rahi hain
        for key, value in request.POST.items():
            if key.startswith('qty_') and value and value != '0':
                item_id = key.replace('qty_', '') # ID nikalna
                try:
                    item = Inventory.objects.get(item_id=item_id)
                    qty_change = float(value)
                    
                    # Stock Update Logic
                    item.current_stock += qty_change
                    if item.current_stock < 0:
                        item.current_stock = 0
                    
                    # Delivery Status Reset
                    item.is_delivered = False 
                    item.save()
                    updated = True
                except (Inventory.DoesNotExist, ValueError):
                    continue
        
        if updated:
            messages.success(request, "Inventory updated! Delivery status reset.")
        else:
            messages.info(request, "No changes were made.")
            
    return redirect('inventory')


@login_required
def warden_leave_view(request):
    try:
        current_warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        messages.error(request, "Warden profile not found.")
        return redirect('welcome_role')

    if request.method == "POST":
        # HTML form ke name attributes se match karna chahiye
        action_type = request.POST.get('action_type') 
        leave_type = request.POST.get('leave_type')
        start_date_val = request.POST.get('start_date')
        end_date_val = request.POST.get('end_date')
        reason = request.POST.get('reason', '')
        leave_attachment = request.FILES.get('leave_attachment')

        if not leave_attachment:
            messages.error(request, "Please upload an image or PDF before submitting the leave request.")
            return redirect('warden_leave')

        # Basic Date Validation
        try:
            s_date = date.fromisoformat(start_date_val)
            e_date = date.fromisoformat(end_date_val)
        except (ValueError, TypeError):
            messages.error(request, "Invalid date format.")
            return redirect('warden_leave')

        if s_date < date.today():
            messages.error(request, "Past dates are not allowed.")
            return redirect('warden_leave')
        if e_date < s_date:
            messages.error(request, "End date cannot be earlier than start date.")
            return redirect('warden_leave')

        # Logic for Saving
        if action_type == 'self':
            existing_self_leave = LeaveRequest.objects.filter(
                warden=current_warden,
                is_warden_request=True,
                status='Approved',
                start_date__lte=e_date,
                end_date__gte=s_date,
            ).order_by('start_date').first()

            if existing_self_leave:
                messages.error(
                    request,
                    f"You already have an approved leave from {existing_self_leave.start_date} to {existing_self_leave.end_date}. You cannot apply again for these dates."
                )
                return redirect('warden_leave')

            LeaveRequest.objects.create(
                warden=current_warden,
                is_warden_request=True,
                leave_type=leave_type,
                start_date=s_date,
                end_date=e_date,
                reason=reason,
                attachment=leave_attachment,
                status='Pending'
            )
            #admin ko noti
            admin_user = User.objects.filter(is_superuser=True).first()
            
            if admin_user:
                Notification.objects.create(
                    recipient=admin_user,
                    message=f"Warden {current_warden.name} has applied for Self Leave.",
                    noti_type='leave'
                ) # Ek hi bracket yahan band hoga
            
            # Ye line 'if admin_user' ke bahar honi chahiye
            messages.success(request, "Your leave request (Warden) created.")
        else:
            w_id = request.POST.get('worker_id')
            if not w_id:
                messages.error(request, "Please select a worker.")
                return redirect('warden_leave')
                
            try:
                worker_master = UniversityID.objects.get(university_id=w_id, role='worker')
                worker_obj = Worker.objects.filter(worker_id=w_id).first()
                existing_worker_leave = LeaveRequest.objects.filter(
                    worker_master=worker_master,
                    is_warden_request=False,
                    status='Approved',
                    start_date__lte=e_date,
                    end_date__gte=s_date,
                ).order_by('start_date').first()

                if existing_worker_leave:
                    messages.error(
                        request,
                        f"{worker_master.full_name} already has an approved leave from {existing_worker_leave.start_date} to {existing_worker_leave.end_date}. A new request for these dates is not allowed."
                    )
                    return redirect('warden_leave')

                LeaveRequest.objects.create(
                    worker=worker_obj,
                    worker_master=worker_master,
                    warden=current_warden,
                    is_warden_request=False,
                    leave_type=leave_type,
                    start_date=s_date,
                    end_date=e_date,
                    reason=reason,
                    attachment=leave_attachment,
                    status='Pending'
                )
                #admin ko noti jaega 
               # --- 🔔 2. ADMIN NOTIFICATION LOGIC ---
                # Pehle Admin ko fetch karein
                from django.db.models import Q
                admin_user = User.objects.filter(Q(role='admin') | Q(is_superuser=True)).first()

                if admin_user:
                    Notification.objects.create(
                        recipient=admin_user,
                        message=f"Warden {current_warden.name} requested leave for Worker {worker_master.full_name}.",
                        noti_type='leave'
                    )

                # Success message (if admin_user ke bahar, try block ke andar)
                messages.success(request, f"Leave request for {worker_master.full_name} submitted.")

            except UniversityID.DoesNotExist:
                messages.error(request, f"Worker with ID {w_id} not found in the master list.")

        return redirect('warden_leave')

    # GET Request: Data Fetching
    # 'select_related' add kiya hai taaki 'worker.name' loop mein aa sake
    context = {
        'workers': UniversityID.objects.filter(role='worker'), 
        'today': date.today().strftime('%Y-%m-%d'),
        'warden': current_warden,
        'pending': LeaveRequest.objects.filter(warden=current_warden, status='Pending').select_related('worker'),
        'history': LeaveRequest.objects.filter(warden=current_warden).exclude(status='Pending').select_related('worker').order_by('-created_at')
    }
    return render(request, 'Shree1/warden_leave.html', context)


@login_required
def warden_profile(request):
    try:
        warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        return redirect('welcome_role')

    # -------- SAVE DATA --------
    if request.method == "POST":
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        
        if not re.match(r'^[1-9][0-9]{9}$', phone):
            messages.error(request, "Phone number must be 10 digits and cannot start with 0.")
            return redirect('warden_profile')

        # update email in User model
        request.user.email = email
        request.user.phone = phone
        request.user.save()

        # update phone in Warden model
        warden.email = email
        warden.phone_number = phone
        warden.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('warden_profile')

    # -------- DISPLAY DATA --------
    context = {
        "display_name": warden.name,
        "display_role": "Warden",

        "full_name": warden.name,
        "email": request.user.email,
        "phone": warden.phone_number,
        "warden_id": warden.warden_id,
        "joining_date": request.user.date_joined.strftime("%d %B %Y"),
    }

    return render(request, "Shree1/warden_profile.html", context)



@never_cache
def admin_dashboard(request):

    if not request.user.is_authenticated:
        return redirect('admin_login')

    # 1. Fetch Totals for the Statistic Cards
    total_wardens = Warden.objects.count()
    total_workers = Worker.objects.count()
    total_suppliers = Supplier.objects.count()
    
    # 2. Logic for Inventory Alerts (Example: items with stock < 20)
    # If you haven't created an Inventory model yet, we can pass dummy data for now
    # but the counts above are 100% dynamic.
    
    context = {
        'warden_count': total_wardens,
        'worker_count': total_workers,
        'supplier_count': total_suppliers,
        'admin_name': request.user.username, # Shows the logged-in Admin ID/Name
    }
    
    return render(request, 'Shree1/dashboardAdmin.html', context)

# -------------------------------
# 5. LOGIN PAGES (FUNCTIONAL)
# -------------------------------

@never_cache
def worker_login(request):
    if request.method == "POST":
        u_id = request.POST.get('worker_id')  # Matches HTML name="worker_id"
        passw = request.POST.get('password')
        user = authenticate(request, username=u_id, password=passw)
        if user and user.role == 'worker':
            login(request, user)
            return redirect('worker_dashboard')
        messages.error(request, "Invalid Worker Credentials", extra_tags='auth_error')
    return render(request, 'Shree1/loginWorker.html')



@never_cache
def warden_login(request):
    if request.method == "POST":
        u_id = request.POST.get('warden_id') # Matches HTML name="warden_id"
        passw = request.POST.get('password')
        user = authenticate(request, username=u_id, password=passw)
        if user and user.role == 'warden':
            login(request, user)
            return redirect('warden_dashboard')
        messages.error(request, "Invalid Warden Credentials", extra_tags='auth_error')
    return render(request, 'Shree1/loginWarden.html')



#@login_required(login_url='login') 
@never_cache
def supplier_login(request):
    if request.method == "POST":
        u_id = request.POST.get('supplier_id') # Form field name
        passw = request.POST.get('password')
        user = authenticate(request, username=u_id, password=passw)
        
        if user and user.role == 'supplier':
            login(request, user)
            messages.success(request, "Welcome back, Kutir!")
            return redirect('supplier_dashboard')
        
        messages.error(request, "Invalid Credentials for Kutir Supplier.", extra_tags='auth_error')
    return render(request, 'Shree1/loginSupplier.html')




#@login_required
@never_cache
def admin_login(request):
    if request.method == "POST":
        u_id = request.POST.get('user_id') # Matches HTML name="user_id"
        passw = request.POST.get('password')
        user = authenticate(request, username=u_id, password=passw)
        if user and (user.role == 'admin' or user.is_staff):
            login(request, user)
            return redirect('admin_dashboard')
        messages.error(request, "Invalid Admin Credentials", extra_tags='auth_error')
    return render(request, 'Shree1/loginAdmin.html')

def approve_leave_logic(request, leave_request_id):
    leave_req = LeaveRequest.objects.get(id=leave_request_id)
    
    if leave_req.status == 'Pending':
        # Leave days calculate karein (Start aur End date ke beech ka difference)
        delta = leave_req.end_date - leave_req.start_date
        days_requested = delta.days + 1 # +1 kyunki starting day bhi count hota hai

        worker = leave_req.worker
        worker_name = leave_req.display_worker_name

        if worker is None:
            leave_req.status = 'Approved'
            leave_req.save()
            messages.success(request, f"Leave Approved for {worker_name}. No registered worker profile was linked, so no leave balance was deducted.")
            return redirect('admin_dashboard')
        
        # Check karein ki balance bacha hai ya nahi
        if worker.leave_balance >= days_requested:
            # 1. Balance deduct karein
            worker.leave_balance -= days_requested
            worker.save()
            
            # 2. Status update karein
            leave_req.status = 'Approved'
            leave_req.save()
            
            messages.success(request, f"Leave Approved! {days_requested} days deducted from {worker_name}'s balance.")
        else:
            # Agar balance kam hai
            messages.error(request, f"Insufficient Balance! {worker_name} only has {worker.leave_balance} leaves left.")
            leave_req.status = 'Rejected'
            leave_req.save()
            
    return redirect('admin_dashboard') # Ya jahan aapka admin dashboard ho

def forget_password(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        selected_question = request.POST.get('security_question', '').strip()
        entered_answer = request.POST.get('security_answer', '').strip()
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        password_error = validate_password(new_password, confirm_password)
        if password_error:
            messages.error(request, password_error)
            return render(request, 'Shree1/forget_password.html')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return render(request, 'Shree1/forget_password.html')

        if user.role not in ['worker', 'warden']:
            messages.error(request, "Password reset is available only for worker and warden accounts.")
            return render(request, 'Shree1/forget_password.html')

        if user.security_question != selected_question:
            messages.error(request, "Wrong security question selected. Please try again.")
            return render(request, 'Shree1/forget_password.html')

        if not user.security_answer or user.security_answer.strip() != entered_answer:
            messages.error(request, "Wrong security answer. Please try again.")
            return render(request, 'Shree1/forget_password.html')

        user.set_password(new_password)
        user.save()
        messages.success(request, "Password reset successful. Please log in with your new password.")

        if user.role == 'warden':
            return redirect('warden_login')
        return redirect('worker_login')

    return render(request, 'Shree1/forget_password.html')






import random
import numpy as np # AI calculations ke liye
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Inventory, DeliveryOrder

# --- 1. AI PREDICTION LOGIC ---
def predict_stock_requirement(item_id):
    item = Inventory.objects.get(item_id=item_id)
    # AI Logic: Agar stock 20% se kam hai, toh high priority dispatch
    stock_ratio = (item.current_stock / item.required_stock) * 100
    
    if stock_ratio < 20:
        return "CRITICAL: Urgent Dispatch Needed"
    return "STABLE: Regular Dispatch"

# --- 2. AI DISPATCH & AUTO-OTP ---
import random
from django.shortcuts import redirect
from django.contrib import messages
from .models import Inventory, DeliveryOrder

def supplier_dispatch_item(request):
    if request.method == "POST":
        # 1. JS ne jo checkboxes select kiye unki IDs uthao
        selected_ids = request.POST.getlist('selected_items')
        
        if not selected_ids:
            messages.error(request, "Please select at least one item.")
            return redirect('supplier_dashboard')

        # 2. Batch ke liye Single OTP (Warden ko dikhane ke liye)
        batch_otp = str(random.randint(100000, 999999))
        any_saved = False

        for item_id in selected_ids:
            # 3. Har item ki quantity uski specific ID se uthao
            qty_val = request.POST.get(f'qty_{item_id}')
            
            if qty_val and float(qty_val) > 0:
                try:
                    inventory_item = Inventory.objects.get(item_id=item_id)
                    
                    # 🔹 AI LOGIC: Stock Condition Check 🔹
                    # Agar stock 20% se kam hai toh AI remark badal jayega
                    stock_ratio = (inventory_item.current_stock / inventory_item.required_stock) * 100
                    ai_suggestion = "CRITICAL: Urgent Delivery" if stock_ratio < 20 else "STABLE: Regular Supply"

                    # 4. Database mein Create karna
                    DeliveryOrder.objects.create(
                        item=inventory_item,
                        qty_delivered=float(qty_val),
                        otp=batch_otp,
                        status='DISPATCHED',
                        ai_remark=ai_suggestion # AI Remark save ho raha hai
                    )
                    any_saved = True
                except Inventory.DoesNotExist:
                    continue

        if any_saved:
            messages.success(request, "Batch dispatched successfully! Please ask the Warden for the verification OTP at the gate.")
        else:
            messages.warning(request, "Quantities were missing or invalid.")

    return redirect('supplier_dashboard')



def supplier_confirm_delivery(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp_code')
        
        # OTP Match Check
        orders = DeliveryOrder.objects.filter(otp=entered_otp, status='DISPATCHED')

        if orders.exists():
            for order in orders:
                # 🔹 AI STOCK UPDATION 🔹
                # Purana stock + New delivery = Updated Inventory
                inventory_item = order.item
                inventory_item.current_stock += order.qty_delivered
                inventory_item.save()

                # Status mark as verified by AI logic
                order.status = 'DELIVERED'
                order.save()

            messages.success(request, "Verification Successful: Inventory Synced.")
        else:
            messages.error(request, "Security Alert: Invalid OTP Attempt.")
        
        # OTP match hone aur inventory.save() hone ke baad:
        admin_user = User.objects.filter(is_superuser=True).first()
        Notification.objects.create(
            recipient=admin_user,
            message=f"Delivery Received: {order.qty_delivered} {inventory_item.unit} of {inventory_item.item_name} added to stock.",
            noti_type='inventory' # Green icon for stock update
            )
            
    return redirect('supplier_dashboard')




from .models import Warden, Worker, LeaveRequest, Inventory, DeliveryOrder # DeliveryOrder import karein


def warden_dashboard(request):

    if not request.user.is_authenticated:
        return redirect('warden_login')

    try:
        warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        return redirect('warden_login')

    # 1. DATA FETCHING
    worker_count = Worker.objects.count()
    
    # 2. LEAVE REQUESTS
    pending_requests = LeaveRequest.objects.filter(status='Pending').order_by('-created_at')[:3]
    pending_count = LeaveRequest.objects.filter(status='Pending').count()

    # 3. 🔹 INCOMING SHIPMENTS & OTP LOGIC 🔹
    # Hum 'DISPATCHED' status waale orders fetch kar rahe hain jo raste mein hain
    incoming_shipments = DeliveryOrder.objects.filter(status='DISPATCHED').order_by('-created_at')

    # 4. LOW STOCK LOGIC
    # Static data ki jagah ab hum original items fetch kar sakte hain
    low_stock_items = []
    all_inventory = Inventory.objects.all()
    for item in all_inventory:
        if item.current_stock < (item.required_stock * 0.5): # 50% threshold
            low_stock_items.append({
                'name': item.item_name,
                'current': item.current_stock,
                'required': item.required_stock,
                'percent': (item.current_stock / item.required_stock) * 100
            })

    # 5. RENDER WITH CONTEXT
    return render(request, 'Shree1/dashboardWarden.html', {
        'warden': warden,
        'worker_count': worker_count,
        'pending_requests': pending_requests,
        'pending_count': pending_count,
        'incoming_shipments': incoming_shipments, # 👈 Yeh HTML mein OTP dikhayega
        'low_stock_items': low_stock_items,
    })
    
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd


def _store_generated_report(request, *, title, report_type, filename, content_bytes):
    GeneratedReport.objects.create(
        title=title,
        report_type=report_type,
        generated_by=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
        file=ContentFile(content_bytes, name=filename),
    )


def worker_report(request):
    workers = UniversityID.objects.filter(role='worker').order_by('full_name')
    report_data = []

    for worker in workers:
        attendance = Attendance.objects.filter(worker_master=worker)
        report_data.append({
            'id': worker.id,
            'worker_name': worker.full_name,
            'present': attendance.filter(status='Present').count(),
            'absent': attendance.filter(status='Absent').count(),
        })

    return render(request, 'Shree1/worker_report.html', {
        'workers': report_data
    })


def download_worker_report(request):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    generated_on = date.today()

    elements.append(Paragraph("Worker Attendance Report", styles['Title']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Date: {generated_on}", styles['Normal']))
    elements.append(Spacer(1, 20))

    data = [['Worker Name', 'Present', 'Absent']]

    workers = UniversityID.objects.filter(role='worker').order_by('full_name')
    for worker in workers:
        attendance = Attendance.objects.filter(worker_master=worker)
        data.append([
            worker.full_name,
            attendance.filter(status='Present').count(),
            attendance.filter(status='Absent').count(),
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)

    pdf_bytes = buffer.getvalue()
    filename = f"worker_report_{generated_on.strftime('%Y%m%d')}.pdf"
    _store_generated_report(
        request,
        title=f"Worker Attendance Report - {generated_on}",
        report_type='summary_pdf',
        filename=filename,
        content_bytes=pdf_bytes,
    )

    admin_user = User.objects.filter(role='admin').first() or User.objects.filter(is_superuser=True).first()
    if admin_user:
        Notification.objects.create(
            recipient=admin_user,
            message=f"Attendance Report was generated and saved on {generated_on}.",
            noti_type='report'
        )

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def worker_chart(request, worker_id):
    worker = get_object_or_404(UniversityID, id=worker_id, role='worker')

    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))

    records = Attendance.objects.filter(
        worker_master=worker,
        date__month=month,
        date__year=year
    ).order_by('date')

    dates = []
    status = []

    for record in records:
        dates.append(record.date.strftime("%d %b"))
        status.append(record.status)

    context = {
        'worker': worker,
        'worker_name': worker.full_name,
        'dates': dates,
        'status': status,
    }

    return render(request, 'Shree1/worker_chart.html', context)


def export_worker_excel(request, worker_id):
    worker = get_object_or_404(UniversityID, id=worker_id, role='worker')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    records = Attendance.objects.filter(
        worker_master=worker,
        date__range=[start_date, end_date]
    ).order_by('date')

    data = []
    for record in records:
        data.append({
            'Date': record.date,
            'Status': record.status
        })

    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    excel_bytes = buffer.getvalue()

    safe_name = worker.full_name.replace(' ', '_')
    filename = f"{safe_name}_{start_date}_to_{end_date}.xlsx"
    _store_generated_report(
        request,
        title=f"{worker.full_name} Attendance Report ({start_date} to {end_date})",
        report_type='worker_excel',
        filename=filename,
        content_bytes=excel_bytes,
    )

    response = HttpResponse(
        excel_bytes,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def forget_password(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        selected_question = request.POST.get('security_question', '').strip()
        entered_answer = request.POST.get('security_answer', '').strip()
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        password_error = validate_password(new_password, confirm_password)
        if password_error:
            messages.error(request, password_error)
            return render(request, 'Shree1/forget_password.html')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return render(request, 'Shree1/forget_password.html')

        if user.role not in ['worker', 'warden']:
            messages.error(request, "Password reset is available only for worker and warden accounts.")
            return render(request, 'Shree1/forget_password.html')

        if user.security_question != selected_question:
            messages.error(request, "Wrong security question selected. Please try again.")
            return render(request, 'Shree1/forget_password.html')

        if not user.security_answer or user.security_answer.strip() != entered_answer:
            messages.error(request, "Wrong security answer. Please try again.")
            return render(request, 'Shree1/forget_password.html')

        user.set_password(new_password)
        user.save()
        messages.success(request, "Password reset successful. Please log in with your new password.")

        if user.role == 'warden':
            return redirect('warden_login')
        return redirect('worker_login')

    return render(request, 'Shree1/forget_password.html')






import random
import numpy as np # AI calculations ke liye
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Inventory, DeliveryOrder

# --- 1. AI PREDICTION LOGIC ---
def predict_stock_requirement(item_id):
    item = Inventory.objects.get(item_id=item_id)
    # AI Logic: Agar stock 20% se kam hai, toh high priority dispatch
    stock_ratio = (item.current_stock / item.required_stock) * 100
    
    if stock_ratio < 20:
        return "CRITICAL: Urgent Dispatch Needed"
    return "STABLE: Regular Dispatch"

# --- 2. AI DISPATCH & AUTO-OTP ---
import random
from django.shortcuts import redirect
from django.contrib import messages
from .models import Inventory, DeliveryOrder

def supplier_dispatch_item(request):
    if request.method == "POST":
        # 1. JS ne jo checkboxes select kiye unki IDs uthao
        selected_ids = request.POST.getlist('selected_items')
        
        if not selected_ids:
            messages.error(request, "Please select at least one item.")
            return redirect('supplier_dashboard')

        # 2. Batch ke liye Single OTP (Warden ko dikhane ke liye)
        batch_otp = str(random.randint(100000, 999999))
        any_saved = False

        for item_id in selected_ids:
            # 3. Har item ki quantity uski specific ID se uthao
            qty_val = request.POST.get(f'qty_{item_id}')
            
            if qty_val and float(qty_val) > 0:
                try:
                    inventory_item = Inventory.objects.get(item_id=item_id)
                    
                    # 🔹 AI LOGIC: Stock Condition Check 🔹
                    # Agar stock 20% se kam hai toh AI remark badal jayega
                    stock_ratio = (inventory_item.current_stock / inventory_item.required_stock) * 100
                    ai_suggestion = "CRITICAL: Urgent Delivery" if stock_ratio < 20 else "STABLE: Regular Supply"

                    # 4. Database mein Create karna
                    DeliveryOrder.objects.create(
                        item=inventory_item,
                        qty_delivered=float(qty_val),
                        otp=batch_otp,
                        status='DISPATCHED',
                        ai_remark=ai_suggestion # AI Remark save ho raha hai
                    )
                    any_saved = True
                except Inventory.DoesNotExist:
                    continue

        if any_saved:
            messages.success(request, "Batch dispatched successfully! Please ask the Warden for the verification OTP at the gate.")
        else:
            messages.warning(request, "Quantities were missing or invalid.")

    return redirect('supplier_dashboard')



def supplier_confirm_delivery(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp_code')
        
        # OTP Match Check
        orders = DeliveryOrder.objects.filter(otp=entered_otp, status='DISPATCHED')

        if orders.exists():
            for order in orders:
                # 🔹 AI STOCK UPDATION 🔹
                # Purana stock + New delivery = Updated Inventory
                inventory_item = order.item
                inventory_item.current_stock += order.qty_delivered
                inventory_item.save()

                # Status mark as verified by AI logic
                order.status = 'DELIVERED'
                order.save()

            messages.success(request, "Verification Successful: Inventory Synced.")
        else:
            messages.error(request, "Security Alert: Invalid OTP Attempt.")
        
        # OTP match hone aur inventory.save() hone ke baad:
        admin_user = User.objects.filter(is_superuser=True).first()
        Notification.objects.create(
            recipient=admin_user,
            message=f"Delivery Received: {order.qty_delivered} {inventory_item.unit} of {inventory_item.item_name} added to stock.",
            noti_type='inventory' # Green icon for stock update
            )
            
    return redirect('supplier_dashboard')




from .models import Warden, Worker, LeaveRequest, Inventory, DeliveryOrder # DeliveryOrder import karein


def warden_dashboard(request):

    if not request.user.is_authenticated:
        return redirect('warden_login')

    try:
        warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        return redirect('warden_login')

    # 1. DATA FETCHING
    worker_count = Worker.objects.count()
    
    # 2. LEAVE REQUESTS
    pending_requests = LeaveRequest.objects.filter(status='Pending').order_by('-created_at')[:3]
    pending_count = LeaveRequest.objects.filter(status='Pending').count()

    # 3. 🔹 INCOMING SHIPMENTS & OTP LOGIC 🔹
    # Hum 'DISPATCHED' status waale orders fetch kar rahe hain jo raste mein hain
    incoming_shipments = DeliveryOrder.objects.filter(status='DISPATCHED').order_by('-created_at')

    # 4. LOW STOCK LOGIC
    # Static data ki jagah ab hum original items fetch kar sakte hain
    low_stock_items = []
    all_inventory = Inventory.objects.all()
    for item in all_inventory:
        if item.current_stock < (item.required_stock * 0.5): # 50% threshold
            low_stock_items.append({
                'name': item.item_name,
                'current': item.current_stock,
                'required': item.required_stock,
                'percent': (item.current_stock / item.required_stock) * 100
            })

    # 5. RENDER WITH CONTEXT
    return render(request, 'Shree1/dashboardWarden.html', {
        'warden': warden,
        'worker_count': worker_count,
        'pending_requests': pending_requests,
        'pending_count': pending_count,
        'incoming_shipments': incoming_shipments, # 👈 Yeh HTML mein OTP dikhayega
        'low_stock_items': low_stock_items,
    })
    
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd


def _store_generated_report(request, *, title, report_type, filename, content_bytes):
    GeneratedReport.objects.create(
        title=title,
        report_type=report_type,
        generated_by=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
        file=ContentFile(content_bytes, name=filename),
    )


def worker_report(request):
    workers = UniversityID.objects.filter(role='worker').order_by('full_name')
    report_data = []

    for worker in workers:
        attendance = Attendance.objects.filter(worker_master=worker)
        report_data.append({
            'id': worker.id,
            'worker_name': worker.full_name,
            'present': attendance.filter(status='Present').count(),
            'absent': attendance.filter(status='Absent').count(),
        })

    return render(request, 'Shree1/worker_report.html', {
        'workers': report_data
    })


def download_worker_report(request):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    generated_on = date.today()

    elements.append(Paragraph("Worker Attendance Report", styles['Title']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Date: {generated_on}", styles['Normal']))
    elements.append(Spacer(1, 20))

    data = [['Worker Name', 'Present', 'Absent']]

    workers = UniversityID.objects.filter(role='worker').order_by('full_name')
    for worker in workers:
        attendance = Attendance.objects.filter(worker_master=worker)
        data.append([
            worker.full_name,
            attendance.filter(status='Present').count(),
            attendance.filter(status='Absent').count(),
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)

    pdf_bytes = buffer.getvalue()
    filename = f"worker_report_{generated_on.strftime('%Y%m%d')}.pdf"
    _store_generated_report(
        request,
        title=f"Worker Attendance Report - {generated_on}",
        report_type='summary_pdf',
        filename=filename,
        content_bytes=pdf_bytes,
    )

    admin_user = User.objects.filter(role='admin').first() or User.objects.filter(is_superuser=True).first()
    if admin_user:
        Notification.objects.create(
            recipient=admin_user,
            message=f"Attendance Report was generated and saved on {generated_on}.",
            noti_type='report'
        )

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def worker_chart(request, worker_id):
    worker = get_object_or_404(UniversityID, id=worker_id, role='worker')

    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))

    records = Attendance.objects.filter(
        worker_master=worker,
        date__month=month,
        date__year=year
    ).order_by('date')

    dates = []
    status = []

    for record in records:
        dates.append(record.date.strftime("%d %b"))
        status.append(record.status)

    context = {
        'worker': worker,
        'worker_name': worker.full_name,
        'dates': dates,
        'status': status,
    }

    return render(request, 'Shree1/worker_chart.html', context)


def export_worker_excel(request, worker_id):
    worker = get_object_or_404(UniversityID, id=worker_id, role='worker')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    records = Attendance.objects.filter(
        worker_master=worker,
        date__range=[start_date, end_date]
    ).order_by('date')

    data = []
    for record in records:
        data.append({
            'Date': record.date,
            'Status': record.status
        })

    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    excel_bytes = buffer.getvalue()

    safe_name = worker.full_name.replace(' ', '_')
    filename = f"{safe_name}_{start_date}_to_{end_date}.xlsx"
    _store_generated_report(
        request,
        title=f"{worker.full_name} Attendance Report ({start_date} to {end_date})",
        report_type='worker_excel',
        filename=filename,
        content_bytes=excel_bytes,
    )

    response = HttpResponse(
        excel_bytes,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


from django.contrib.auth import logout


def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('welcome_role')



def admin_inventory(request):
    items = Inventory.objects.all()
    critical_count = sum(1 for item in items if item.get_status == "Critical")
    low_count = sum(1 for item in items if item.get_status == "Low")
    recent_usage = DailyUsage.objects.select_related('item').order_by('-date', '-id')[:10]

    context = {
        'items': items,
        'critical_count': critical_count,
        'low_count': low_count,
        'recent_usage': recent_usage,
    }
    return render(request, 'Shree1/admin_inventory.html', context)
