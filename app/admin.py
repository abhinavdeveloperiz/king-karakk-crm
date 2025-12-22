from django.contrib import admin

# Register your models here.
from .models import User, Branch, Transaction, SalesCategory, PurchaseCategory, ExpenseCategory

admin.site.register(User)
admin.site.register(Branch)
admin.site.register(Transaction)
admin.site.register(SalesCategory)
admin.site.register(PurchaseCategory)
admin.site.register(ExpenseCategory)