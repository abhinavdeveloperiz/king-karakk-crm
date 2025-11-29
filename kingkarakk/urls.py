from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [

    # ================== ADMIN  ==================
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/profile/', views.admin_profile, name='admin_profile'),

    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/daily-sales/', views.daily_sales_report, name='daily_sales_report'),

    path('admin/branch/list/', views.branch_list, name='branch_list'),
    path('admin/branch/add/', views.branch_add, name='branch_add'),
    path('admin/branch/edit/', views.branch_edit, name='branch_edit'),
    path('admin/branch/detail/', views.branch_detail, name='branch_detail'),
    path('admin/branch/delete/<int:branch_id>/', views.branch_delete, name='branch_delete'),
    path('admin/branch/financial-overview/', views.branch_financial_overview, name='branch_financial_overview'),
    path('admin/business-overview/', views.business_overview, name='business_overview'),



    # ================== BRANCH  ==================
    path('branch/login/', views.branch_login, name='branch_login'),

    path('', views.branch_dashboard, name='branch_dashboard'),
    path('branch/expense-entry/', views.branch_expense_sales_entry, name='branch_expense_sales_entry'),
    path('branch/profile/', views.branch_profile, name='branch_profile'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

