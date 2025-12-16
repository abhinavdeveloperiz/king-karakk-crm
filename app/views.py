from django.shortcuts import render,redirect,get_object_or_404
from .forms import BranchCreateForm,BranchEditForm
from .models import Branch,User,Transaction

# branch forms 
from .forms import BranchTransactionCreateForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone

import json






def admin_and_branch_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect("admin_dashboard")   
            elif getattr(user, "is_branch", False):
                return redirect("branch_dashboard") 
            else:
                # Normal users not allowed
                error = "You are not allowed to login here."
                return render(request, "owner/login.html", {"error": error})
        else:
            error = "Invalid username or password."
            return render(request, "owner/login.html", {"error": error})
    
    return render(request, "owner/login.html")


def admin_and_branch_logout(request):
    logout(request)
    return redirect("login")

@login_required(login_url="login")
def admin_profile(request):
    return render(request, 'owner/admin_profile.html')

@login_required(login_url="login")
def admin_dashboard(request):
    return render(request, 'owner/admin_dashboard.html')

@login_required(login_url="login")
def daily_sales_report(request):
    return render(request, 'owner/daily_sales_report.html')

@login_required(login_url="login")
def Admin_cashflow(request):
    return render(request, 'owner/admin_cashflow.html')
    



# -------------------------------------------------------------- 

@login_required(login_url="login")
def branch_list(request):
    branches = Branch.objects.select_related('user').all()
    return render(request, 'owner/admin_branch_list.html', {"branches": branches})



@login_required(login_url="login")
def branch_add(request):
    if request.method == "POST":
        form = BranchCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("branch_list") 
    else:
        form = BranchCreateForm()

    return render(request, 'owner/admin_branch_add.html', {"form": form})



@login_required(login_url="login")
def branch_edit(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    user = branch.user

    if request.method == "POST":
        form = BranchEditForm(request.POST)
        if form.is_valid():
            user.username = form.cleaned_data["username"]

            new_password = form.cleaned_data["password"]
            if new_password.strip() != "":
                user.password = make_password(new_password)

            user.save()

            # Update branch
            branch.name = form.cleaned_data["name"]
            branch.location = form.cleaned_data["location"]
            branch.save()

            return redirect("branch_list")

    else:
        form = BranchEditForm(initial={
            "name": branch.name,
            "location": branch.location,
            "username": user.username,
        })

    return render(request, "owner/admin_branch_edit.html", {
        "form": form,
        "branch": branch
    })

@login_required(login_url="login")
def branch_delete(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    user = branch.user

    user.delete()   
    return redirect("branch_list")



@login_required(login_url="login")
def branch_detail(request):
    return render(request, 'owner/admin_branch_detail.html')




def branch_financial_overview(request):
    return render(request, 'owner/branch_financial_overview.html')

def business_overview(request):
    return render(request, 'owner/business_overview.html')



# --------------------------------------------------------------------------- 







@login_required(login_url="login")
def branch_dashboard(request):
    try:
        branch = request.user.branch_account
    except Branch.DoesNotExist:
        branch = None

    today = timezone.localdate()

    if branch:
        transactions = branch.transactions.filter(created_on__date=today)

        totals = transactions.aggregate(
            total_sales=Sum('sales'),
            total_expense=Sum('expense'),
            total_purchase=Sum('purchase')
        )

        total_sales = totals.get('total_sales') or Decimal('0.00')
        total_expense = totals.get('total_expense') or Decimal('0.00')
        total_purchase = totals.get('total_purchase') or Decimal('0.00')
        balance_total = total_sales - total_expense - total_purchase

        chart_data = {
            'labels': ['Sales', 'Expenses', 'Purchase'],
            'values': [float(total_sales), float(total_expense), float(total_purchase)]
        }

    else:
        total_sales = total_expense = total_purchase = balance_total = 0
        chart_data = {'labels': [], 'values': []}

    context = {
        'branch': branch,
        'today': today,
        'total_sales': total_sales,
        'total_expense': total_expense,
        'total_purchase': total_purchase,
        'balance_total': balance_total,
        'chart_data_json': json.dumps(chart_data)
    }

    return render(request, 'branch/branch_dashboard.html', context)





@login_required(login_url="login")
def branch_expense_sales_list(request):
   
    try:
        branch = request.user.branch_account
    except Branch.DoesNotExist:
        messages.error(request, "You do not have a branch assigned. Please contact admin.")
        return redirect("branch_dashboard")
    
    today = timezone.localdate() 

    transactions = branch.transactions.filter(created_on__date=today).order_by('-created_on')

    totals = transactions.aggregate(
        total_sales=Sum('sales'),
        total_expense=Sum('expense'),
        total_purchase=Sum('purchase')
    )

    total_sales = totals.get('total_sales') or Decimal('0.00')
    total_expense = totals.get('total_expense') or Decimal('0.00')
    total_purchase = totals.get('total_purchase') or Decimal('0.00')

    balance_total = total_sales - total_expense - total_purchase

    context = {
        "transactions": transactions,
        "branch": branch,
        "total_sales": total_sales,
        "total_expense": total_expense,
        "total_purchase": total_purchase,
        "balance_total": balance_total,
        "today": today,
    }

    return render(request, "branch/branch_expense_sales.html", context)



@login_required(login_url="login")
def branch_expense_sales_entry(request):
    try:
        branch = request.user.branch_account  
    except Branch.DoesNotExist:
        messages.error(request, "You do not have a branch assigned. Please contact admin.")
        return redirect("branch_dashboard") 

    if request.method == "POST":
        form = BranchTransactionCreateForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.branch = branch
            transaction.save()
            messages.success(request, "Transaction added successfully.") 
            return redirect("branch_expense_sales_list")
    else:
        form = BranchTransactionCreateForm()
    
    return render(request, "branch/branch_expense_sales_add.html", {"form": form})



@login_required(login_url="login")
def branch_profile(request):
    return render(request, 'branch/branch_profile.html')

