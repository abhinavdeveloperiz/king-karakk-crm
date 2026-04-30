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
    working_partnership = models.DecimalField(max_digits=5,  decimal_places=2,help_text="Enter percentage like 2.50 for 2.5%")
    
    def __str__(self):
        return self.name
    





class Transaction(models.Model):
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

    CASHBALANCE_CATEGORY_CHOICES = (
        ("OPENING", "Opening Balance"),
        ("CLOSING", "Closing Balance"),
        ('OTHER', 'Other'),
    )

    TRANSACTION_TYPE_CHOICES = (
        ("SALE", "Sales"),
        ("PURCHASE", "Purchase"),
        ("EXPENSE", "Expense"),
        ("CASHBALANCE", "Cash Balance"),
        ("TRANSFER", "Transfer"),
    )


    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="transactions"
    )

    target_branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_transfers"
    )

    transaction_type = models.CharField(max_length=12, choices=TRANSACTION_TYPE_CHOICES
    )

   

    purchase_category = models.CharField(max_length=30, choices=PURCHASE_CATEGORY_CHOICES,null=True,blank=True
    )

    expense_category = models.CharField(max_length=30, choices=EXPENSE_CATEGORY_CHOICES,null=True,blank=True
    )

    cashbalance_category = models.CharField(max_length=30, choices=CASHBALANCE_CATEGORY_CHOICES,null=True,blank=True
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.branch.name} - {self.transaction_type} - {self.amount}"


   
