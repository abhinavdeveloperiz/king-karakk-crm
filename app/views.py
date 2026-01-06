from django.shortcuts import render,redirect,get_object_or_404
from .forms import BranchCreateForm,BranchEditForm
from .models import Branch,User,Transaction
from django.contrib.auth import update_session_auth_hash

# branch forms 
from .forms import BranchTransactionCreateForm

from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.db.models import Sum, Case, When, DecimalField
from django.db.models.functions import TruncDate
from decimal import Decimal

from django.core.paginator import Paginator




from collections import defaultdict
from django.utils import timezone
from django.utils.timezone import now
import json
from datetime import datetime, time








def admin_and_branch_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("admin_dashboard")
        elif getattr(request.user, "is_branch", False):
            return redirect("branch_dashboard")
        else:
            logout(request)

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect("login")   # IMPORTANT: redirect, not render

        if not (user.is_superuser or getattr(user, "is_branch", False)):
            messages.error(request, "You are not allowed to login here.")
            return redirect("login")

        login(request, user)

        return redirect(
            "admin_dashboard" if user.is_superuser else "branch_dashboard"
        )

    return render(request, "auth/login.html")





@login_required(login_url="login")
def change_superadmin_credentials(request):
    user = request.user

    if not user.is_superuser:
        return redirect("login")

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_username = request.POST.get("new_username", "").strip()
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # 1️⃣ Old password check
        if not user.check_password(old_password):
            messages.error(request, "Old password is incorrect.")
            return redirect("change_credentials")

        # 2️⃣ Password confirmation
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("change_credentials")

        # 3️⃣ No-change validation
        username_unchanged = new_username == user.username
        password_unchanged = user.check_password(new_password)

        if username_unchanged and password_unchanged:
            messages.error(
                request,
                "New username and password must be different from the current credentials."
            )
            return redirect("change_credentials")
        

        if new_username and not username_unchanged:
            user.username = new_username

        # 5️⃣ Update password if changed
        if not password_unchanged:
            user.set_password(new_password)

        user.save()
        update_session_auth_hash(request, user)

        messages.success(request, "Admin credentials updated successfully.")
        return redirect("admin_profile")

    return render(request, "auth/change_credentials.html")





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
    today = timezone.localdate()

    start_of_day = timezone.make_aware(datetime.combine(today, time.min))
    end_of_day = timezone.make_aware(datetime.combine(today, time.max))

    transactions = (
        Transaction.objects
        .select_related("branch")
        .filter(created_on__range=(start_of_day, end_of_day))
        .order_by("branch__name", "created_on")
    )

    branch_data = {}

    for tx in transactions:
        branch = tx.branch

        if branch not in branch_data:
            branch_data[branch] = {
                "transactions": [],
                "balance": Decimal("0.00"),
            }

        branch_data[branch]["transactions"].append(tx)

        if tx.transaction_type == "SALE":
            branch_data[branch]["balance"] += tx.amount
        else:  # EXPENSE or PURCHASE
            branch_data[branch]["balance"] -= tx.amount

    context = {
        "today": today,
        "branch_data": branch_data,
    }

    return render(request, "owner/daily_sales_report.html", context)











from django.db.models import Sum, Case, When, DecimalField
from decimal import Decimal
from datetime import date
import calendar

from .models import Transaction, Branch


@login_required(login_url="login")
def Admin_cashflow(request):

    # ---------------- FILTERS ----------------
    branch_id = request.GET.get("branch", "all")
    month = request.GET.get("month")  # YYYY-MM

    qs = Transaction.objects.select_related("branch")

    # Branch filter
    if branch_id != "all":
        qs = qs.filter(branch_id=branch_id)

    # Month filter (SAFE DATE RANGE FILTER)
    if month:
        year, mon = map(int, month.split("-"))

        start_date = date(year, mon, 1)
        last_day = calendar.monthrange(year, mon)[1]
        end_date = date(year, mon, last_day)

        qs = qs.filter(created_on__date__range=(start_date, end_date))

    # ---------------- SUMMARY TABLE ----------------
    summary = (
        qs.values("created_on__date", "branch__name")
        .annotate(
            sales=Sum(
                Case(
                    When(transaction_type="SALE", then="amount"),
                    default=Decimal("0.00"),
                    output_field=DecimalField(),
                )
            ),
            expense=Sum(
                Case(
                    When(transaction_type="EXPENSE", then="amount"),
                    default=Decimal("0.00"),
                    output_field=DecimalField(),
                )
            ),
            purchase=Sum(
                Case(
                    When(transaction_type="PURCHASE", then="amount"),
                    default=Decimal("0.00"),
                    output_field=DecimalField(),
                )
            ),
        )
        .order_by("created_on__date", "branch__name")
    )

    grand_total = Decimal("0.00")

    for row in summary:
        net = (row["sales"] or 0) - ((row["expense"] or 0) + (row["purchase"] or 0))
        row["net_cash"] = net
        row["net_display"] = abs(net)
        row["is_positive"] = net >= 0
        grand_total += net

    # ---------------- TRANSACTION LIST ----------------
    transaction_list = qs.order_by("-created_on")
    paginator = Paginator(transaction_list, 30)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "summary": summary,
        "transactions": page_obj,
        "branches": Branch.objects.all(),
        "selected_branch": branch_id,
        "selected_month": month,
        "grand_total": grand_total,
        "query_string": request.GET.urlencode(),
    }

    return render(request, "owner/admin_cashflow.html", context)








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
def branch_detail(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    today = timezone.localdate()

    start_of_day = timezone.make_aware(datetime.combine(today, time.min))
    end_of_day = timezone.make_aware(datetime.combine(today, time.max))
   
    today_transactions = Transaction.objects.filter(
        branch=branch,
        created_on__gte=start_of_day, created_on__lte=end_of_day
    ).order_by("-created_on")

   


    today_sales = today_transactions.filter(
        transaction_type="SALE"
    ).aggregate(total=Sum("amount"))["total"] or 0

    today_expenses = today_transactions.filter(
        transaction_type="EXPENSE"
    ).aggregate(total=Sum("amount"))["total"] or 0

    today_purchases = today_transactions.filter(
        transaction_type="PURCHASE"
    ).aggregate(total=Sum("amount"))["total"] or 0

  

    today_balance = today_sales - (today_expenses + today_purchases)

    context = {
        "branch": branch,
        "today_transactions": today_transactions,
        "today_sales": today_sales,
        "today_expenses": today_expenses,
        "today_purchases": today_purchases,
        "today_balance": today_balance,
        "today_date": today,
    }

    return render(request, "owner/admin_branch_detail.html", context)






@login_required(login_url="login")
def admin_add_transaction_to_branch(request, branch_id):
    if not request.user.is_superuser:
        return redirect("login")

    branch = get_object_or_404(Branch, id=branch_id)

    if request.method == "POST":
        form = BranchTransactionCreateForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.branch = branch
            selected_date = form.cleaned_data['created_on']
            transaction.created_on = timezone.make_aware(datetime.combine(selected_date, timezone.now().time()))
            transaction.full_clean()
            transaction.save()
            messages.success(request, f"Transaction added successfully to {branch.name}.")
            return redirect("branch_detail", branch_id=branch_id)
    else:
        form = BranchTransactionCreateForm()

    return render(
        request,
        "owner/admin_add_transaction.html",
        {"form": form, "branch": branch}
    )






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

    total_sales = total_expense = total_purchase = balance_total = Decimal("0.00")
    chart_data = {"labels": [], "values": []}

    if branch:
        start_of_day = timezone.make_aware(datetime.combine(today, time.min))
        end_of_day = timezone.make_aware(datetime.combine(today, time.max))
        transactions = branch.transactions.filter(created_on__gte=start_of_day, created_on__lte=end_of_day)

        totals = transactions.aggregate(
            total_sales=Sum(
                Case(
                    When(transaction_type="SALE", then="amount"),
                    default=Decimal("0.00"),
                    output_field=DecimalField()
                )
            ),
            total_expense=Sum(
                Case(
                    When(transaction_type="EXPENSE", then="amount"),
                    default=Decimal("0.00"),
                    output_field=DecimalField()
                )
            ),
            total_purchase=Sum(
                Case(
                    When(transaction_type="PURCHASE", then="amount"),
                    default=Decimal("0.00"),
                    output_field=DecimalField()
                )
            ),
        )

        total_sales = totals["total_sales"] or Decimal("0.00")
        total_expense = totals["total_expense"] or Decimal("0.00")
        total_purchase = totals["total_purchase"] or Decimal("0.00")

        balance_total = total_sales - total_expense - total_purchase

        chart_data = {
            "labels": ["Sales", "Expenses", "Purchase"],
            "values": [
                float(total_sales),
                float(total_expense),
                float(total_purchase),
            ],
        }

    context = {
        "branch": branch,
        "today": today,
        "total_sales": total_sales,
        "total_expense": total_expense,
        "total_purchase": total_purchase,
        "balance_total": balance_total,
        "chart_data_json": json.dumps(chart_data),
    }

    return render(request, "branch/branch_dashboard.html", context)






@login_required(login_url="login")
def branch_expense_sales_list(request):
    try:
        branch = request.user.branch_account
    except Branch.DoesNotExist:
        messages.error(request, "You do not have a branch assigned.")
        return redirect("branch_dashboard")

    today = timezone.localdate()

    start_of_day = timezone.make_aware(datetime.combine(today, time.min))
    end_of_day = timezone.make_aware(datetime.combine(today, time.max))

    transactions = branch.transactions.filter(
        created_on__gte=start_of_day, created_on__lte=end_of_day
    ).order_by("-created_on")

    sales_transactions = transactions.filter(transaction_type="SALE")
    expense_transactions = transactions.filter(transaction_type="EXPENSE")
    purchase_transactions = transactions.filter(transaction_type="PURCHASE")

    totals = transactions.aggregate(
        total_sales=Sum(
            Case(
                When(transaction_type="SALE", then="amount"),
                default=Decimal("0.00"),
                output_field=DecimalField()
            )
        ),
        total_expense=Sum(
            Case(
                When(transaction_type="EXPENSE", then="amount"),
                default=Decimal("0.00"),
                output_field=DecimalField()
            )
        ),
        total_purchase=Sum(
            Case(
                When(transaction_type="PURCHASE", then="amount"),
                default=Decimal("0.00"),
                output_field=DecimalField()
            )
        ),
    )

    total_sales = totals["total_sales"] or Decimal("0.00")
    total_expense = totals["total_expense"] or Decimal("0.00")
    total_purchase = totals["total_purchase"] or Decimal("0.00")

    balance_total = total_sales - total_expense - total_purchase

    context = {
        "branch": branch,
        "today": today,
        "sales_transactions": sales_transactions,
        "expense_transactions": expense_transactions,
        "purchase_transactions": purchase_transactions,
        "total_sales": total_sales,
        "total_expense": total_expense,
        "total_purchase": total_purchase,
        "balance_total": balance_total,
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
            selected_date = form.cleaned_data['created_on']
            transaction.created_on = timezone.make_aware(datetime.combine(selected_date, timezone.now().time()))
            transaction.full_clean()  # important
            transaction.save()
            messages.success(request, "Transaction added successfully.")
            return redirect("branch_expense_sales_list")
    else:
        form = BranchTransactionCreateForm()

    return render(
        request,
        "branch/branch_expense_sales_add.html",
        {"form": form}
    )





@login_required(login_url="login")
def branch_profile(request):
    branch = Branch.objects.only("id", "name", "location").get(user=request.user)

    recent_transactions = (
        Transaction.objects
        .filter(branch=branch)
        .only(
            "transaction_type",
            "sales_category",
            "purchase_category",
            "expense_category",
            "amount",
            "created_on",
        )
        .order_by("-created_on")[:3]
    )

    return render(
        request,
        "branch/branch_profile.html",
        {
            "branch": branch,
            "recent_transactions": recent_transactions,
        },
    )
