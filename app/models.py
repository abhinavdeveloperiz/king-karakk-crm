from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    is_branch = models.BooleanField(default=False)  
    def __str__(self):
        return self.username



class Branch(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="branch_account")

    def __str__(self):
        return self.name
    


class SalesCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class PurchaseCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name




class Transaction(models.Model):

    SALES_CATEGORY_CHOICES = (
        ("ONLINE", "Online Sales"),
        ("OFFLINE", "Offline Sales"),
        ("WHOLESALE", "Wholesale"),
        ('OTHER', 'Other'),
    )

    PURCHASE_CATEGORY_CHOICES = (
        ("RAW", "Raw Material"),
        ("ASSET", "Asset Purchase"),
        ("INVENTORY", "Inventory"),
        ('OTHER', 'Other'),
    )

    EXPENSE_CATEGORY_CHOICES = (
        ("RENT", "Rent"),
        ("SALARY", "Salary"),
        ("UTILITY", "Utility"),
        ("MARKETING", "Marketing"),
        ('OTHER', 'Other'),
    )


    TRANSACTION_TYPE_CHOICES = (
        ("SALE", "Sales"),
        ("PURCHASE", "Purchase"),
        ("EXPENSE", "Expense"),
    )


    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="transactions"
    )

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES
    )

    sales_category = models.CharField(max_length=30,choices=SALES_CATEGORY_CHOICES,null=True,blank=True
    )

    purchase_category = models.CharField(max_length=30, choices=PURCHASE_CATEGORY_CHOICES,null=True,blank=True
    )

    expense_category = models.CharField(max_length=30, choices=EXPENSE_CATEGORY_CHOICES,null=True,blank=True
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.branch.name} - {self.transaction_type} - {self.amount}"


   
