from django.contrib import admin

# Register your models here.
from .models import User, Branch, Transaction

admin.site.register(User)
admin.site.register(Branch)
admin.site.register(Transaction)