from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ---------- SELECTION / NAVIGATION ----------
    path('', views.welcome_role, name='welcome_role'), # The starting home page
    path('login-selection/', views.login_selection, name='login_selection'),
    path('signup-selection/', views.role_selection, name='role_selection'),

    # ---------- SIGNUP ----------
    path('signup/worker/', views.worker_signup_view, name='worker_signup'),
    path('signup/warden/', views.warden_signup_view, name='warden_signup'),
    #path('signup/supplier/', views.supplier_signup_view, name='supplier_signup'),

    # ---------- LOGIN ----------
    path('login/worker/', views.worker_login, name='worker_login'),
    path('login/warden/', views.warden_login, name='warden_login'),
    path('login/supplier/', views.supplier_login, name='supplier_login'),
    path('login/admin/', views.admin_login, name='admin_login'),

    # ---------- DASHBOARDS ----------
    path('dashboard/worker/', views.worker_dashboard, name='worker_dashboard'),
    path('dashboard/warden/', views.warden_dashboard, name='warden_dashboard'),
    path('dashboard/supplier/', views.supplier_dashboard, name='supplier_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'), # Added for Admin access

    # ---------- FEATURES ----------
    path('worker/profile/', views.worker_profile, name='worker_profile'),
    path('supplier/profile/', views.supplier_profile, name='supplier_profile'),
    path('warden/attendance/', views.attendance_view, name='attendance'),
    path('warden/inventory/', views.inventory_view, name='inventory'),
    path('warden/leave/', views.warden_leave_view, name='warden_leave'),
    path('warden/profile/', views.warden_profile, name='warden_profile'),

    
    path('warden/inventory/update/', views.update_inventory_stock, name='update_inventory_stock'),
    
    # ---------- ADMIN DATA ACTIONS ----------
    path('add-uni-id/', views.add_university_id, name='add_university_id'),
    path('delete-uni-id/<int:pk>/', views.delete_uni_id, name='delete_uni_id'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('forget-password/', views.forget_password, name='forget_password'),


    path('dispatch/', views.supplier_dispatch_item, name='supplier_dispatch_item'),

    path('confirm-delivery/', views.supplier_confirm_delivery, name='supplier_confirm_delivery'),

]
