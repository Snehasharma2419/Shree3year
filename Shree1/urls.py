# Shree1/urls.py
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [


    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 🌐 Public pages
    path('', views.welcome_role, name='welcome_role'),
    path('choose-login/', views.login_selection, name='login_selection'),
    path('choose-signup/', views.role_selection, name='choose_signup'),

    # 🌍 Language
    path('i18n/', include('django.conf.urls.i18n')),

    # 👤 Accounts app (ALL auth, signup, dashboard)
    path('accounts/', include('accounts.urls')),

    # 🔐 Admin
    path('admin/', admin.site.urls),
    
    
    path('Shree-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('Shree-admin/users/', views.admin_user_management, name='admin_user_management'),

    path('Shree-admin/attendance/', views.admin_attendance, name='admin_attendance'),

   path('Shree-admin/inventory/', views.admin_inventory, name='admin_inventory'),
   
   path('Shree-admin/leave/', views.admin_leave_Management, name='admin_leave_Management'),
   
   path('Shree-admin/profile/', views.admin_profile, name='admin_profile'),
   
   #sneha edit
    path('Shree-admin/add-id/', views.add_university_id, name='add_university_id'),
    
    # Delete User ke liye path (Isme <int:id> dena zaroori hai taaki Django ko pata chale kiska ID delete karna hai)
    path('Shree-admin/delete-id/<int:id>/', views.delete_uni_id, name='delete_uni_id'),


    #ayushi
    path('Shree-admin/inventory/', views.admin_inventory, name='admin_inventory'),
    
    # Shree1/urls.py mein add karein
    path('inventory/delete/<str:item_id>/', views.delete_inventory_item, name='delete_inventory_item'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
