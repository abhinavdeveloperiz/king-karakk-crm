from django import forms
from django.contrib.auth.hashers import make_password
from .models import User, Branch,Transaction


class BranchCreateForm(forms.Form):
    name = forms.CharField(max_length=255)
    location = forms.CharField(max_length=255)
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists!")
        return username

    def save(self):
        name = self.cleaned_data["name"]
        location = self.cleaned_data["location"]
        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]

        user = User.objects.create(
            username=username,
            password=make_password(password),
            is_branch=True
        )

        branch = Branch.objects.create(
            name=name,
            location=location,
            user=user
        )

        return branch


class BranchEditForm(forms.Form):
    name = forms.CharField(max_length=255)
    location = forms.CharField(max_length=255)
    username = forms.CharField(max_length=150)
    password = forms.CharField(required=False, widget=forms.PasswordInput)




class BranchTransactionCreateForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["sales", "expense", "purchase", "description"]

        widgets = {
            "sales": forms.NumberInput(attrs={"class": "form-input w-full border-2 rounded-lg p-2", "placeholder": "Enter Sales"}),
            "expense": forms.NumberInput(attrs={"class": "form-input w-full border-2 rounded-lg p-2", "placeholder": "Enter Expense"}),
            "purchase": forms.NumberInput(attrs={"class": "form-input w-full border-2 rounded-lg p-2", "placeholder": "Enter Purchase"}),
            "description": forms.Textarea(attrs={"class": "form-input w-full border-2 rounded-lg p-2", "rows": 2}),
        }