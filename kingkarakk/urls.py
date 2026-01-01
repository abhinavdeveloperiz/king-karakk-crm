from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from app import views
from django.contrib import admin

urlpatterns = [

    path('category/', admin.site.urls),


    # ================== ADMIN  ==================
    path('branch/admin/login/', views.admin_and_branch_login, name='login'),
    path("change-credentials/", views.change_superadmin_credentials, name="change_credentials"),
    path('branch/admin/logout/', views.admin_and_branch_logout, name='logout'),

    path('admin/profile/', views.admin_profile, name='admin_profile'),

    path('', views.admin_dashboard, name='admin_dashboard'),
    path('admin/daily-sales/', views.daily_sales_report, name='daily_sales_report'),
    path('admin/cashflow/', views.Admin_cashflow, name='admin_cashflow'),

    path('admin/branch/list/', views.branch_list, name='branch_list'),
    path('admin/branch/add/', views.branch_add, name='branch_add'),


    path('admin/branch/<int:branch_id>/edit/', views.branch_edit, name='branch_edit'),

    path("branches/<int:branch_id>/", views.branch_detail, name="branch_detail"),

    path('admin/branch/<int:branch_id>/delete/', views.branch_delete, name='branch_delete'),

    path('admin/branch/financial-overview/', views.branch_financial_overview, name='branch_financial_overview'),
    path('admin/business-overview/', views.business_overview, name='business_overview'),



    # ================== BRANCH  ==================

    path('branch/', views.branch_dashboard, name='branch_dashboard'),
    path('branch/expense-entry/list/', views.branch_expense_sales_list, name='branch_expense_sales_list'),
    path('branch/expense-entry/add/', views.branch_expense_sales_entry, name='branch_expense_sales_add'),
    path('branch/profile/', views.branch_profile, name='branch_profile'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

