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
    

class Transaction(models.Model):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    sales = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    expense = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)

    description = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"{self.branch.name} – {self.created_on.date()}"

    @property
    def balance(self):
        # ensure None-safe arithmetic and return Decimal
        s = self.sales if self.sales is not None else Decimal('0.00')
        e = self.expense if self.expense is not None else Decimal('0.00')
        p = self.purchase if self.purchase is not None else Decimal('0.00')
        return s - e - p
    

    def __str__(self):
        return f"{self.branch.name} – {self.created_on.date()}"


   
