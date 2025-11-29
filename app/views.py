from django.shortcuts import render



def admin_login(request):
    return render(request, 'admin/admin_login.html')


def admin_profile(request):
    return render(request, 'admin/admin_profile.html')

def admin_dashboard(request):
    return render(request, 'admin/admin_dashboard.html')


def daily_sales_report(request):
    return render(request, 'admin/daily_sales_report.html')



# -------------------------------------------------------------- 
def branch_list(request):
    return render(request, 'admin/admin_branch_list.html')

def branch_add(request):
    return render(request, 'admin/admin_branch_add.html')

def branch_edit(request):
    return render(request, 'admin/admin_branch_edit.html')

def branch_detail(request):
    return render(request, 'admin/admin_branch_detail.html')


def branch_delete(request, branch_id):
    return render(request, 'admin/admin_branch_delete.html')

def branch_financial_overview(request):
    return render(request, 'admin/branch_financial_overview.html')

def business_overview(request):
    return render(request, 'admin/business_overview.html')



# --------------------------------------------------------------------------- 


def branch_login(request):
    return render(request, 'branch/branch_login.html')


def branch_dashboard(request):
    return render(request, 'branch/branch_dashboard.html')


def branch_expense_sales_entry(request):
    return render(request, 'branch/branch_expense_sales.html')


def branch_profile(request):
    return render(request, 'branch/branch_profile.html')

