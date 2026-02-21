from django import forms
from django.contrib.auth.hashers import make_password
from .models import User, Branch,Transaction
from django.utils import timezone


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=2)
        tomorrow = today + timezone.timedelta(days=2)
        self.fields['created_on'].widget.attrs.update({
            'min': yesterday.isoformat(),
            'max': tomorrow.isoformat(),
        })
        self.initial['created_on'] = today
        
        # Remove SALE option from branch users - sales are auto-calculated
        if 'transaction_type' in self.fields:
            self.fields['transaction_type'].queryset = None  # This won't work for choices
            # Instead, we'll limit choices in the model's __init__ for ModelForm
            choices = [
                ("PURCHASE", "Purchase"),
                ("EXPENSE", "Expense"),
                ("CASHBALANCE", "Cash Balance"),
            ]
            self.fields['transaction_type'].choices = choices

    class Meta:
        model = Transaction
        fields = [
            "transaction_type",
            "purchase_category",
            "expense_category",
            "cashbalance_category",
            "amount",
            "description",
            "created_on",
        ]

        widgets = {
            "transaction_type": forms.Select(
                attrs={"class": "form-input w-full border-2 rounded-lg p-2"}
            ),

            "purchase_category": forms.Select(
                attrs={"class": "form-input w-full border-2 rounded-lg p-2"}
            ),

            "expense_category": forms.Select(
                attrs={"class": "form-input w-full border-2 rounded-lg p-2"}
            ),

            "cashbalance_category": forms.Select(
                attrs={"class": "form-input w-full border-2 rounded-lg p-2"}
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-input w-full border-2 rounded-lg p-2",
                    "placeholder": "Enter Amount"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-input w-full border-2 rounded-lg p-2",
                    "rows": 2
                }
            ),

            "created_on": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-input w-full border-2 rounded-lg p-2"
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        tx_type = cleaned_data.get("transaction_type")

        purchase = cleaned_data.get("purchase_category")
        expense = cleaned_data.get("expense_category")
        cashbalance = cleaned_data.get("cashbalance_category")

        # Clear unused fields
        if tx_type != "PURCHASE":
            cleaned_data["purchase_category"] = None
        if tx_type != "EXPENSE":
            cleaned_data["expense_category"] = None
        if tx_type != "CASHBALANCE":
            cleaned_data["cashbalance_category"] = None

        # Enforce required category
        if tx_type == "PURCHASE" and not purchase:
            self.add_error("purchase_category", "Purchase category is required")

        if tx_type == "EXPENSE" and not expense:
            self.add_error("expense_category", "Expense category is required")

        if tx_type == "CASHBALANCE" and not cashbalance:
            self.add_error("cashbalance_category", "Cash balance category is required")

        return cleaned_data


class AdminBranchTransactionCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date()
        self.initial['created_on'] = today
        
        # Remove SALE option from branch users - sales are auto-calculated
        if 'transaction_type' in self.fields:
            self.fields['transaction_type'].queryset = None  # This won't work for choices
            # Instead, we'll limit choices in the model's __init__ for ModelForm
            choices = [
                ("PURCHASE", "Purchase"),
                ("EXPENSE", "Expense"),
                ("CASHBALANCE", "Cash Balance"),
            ]
            self.fields['transaction_type'].choices = choices

    class Meta:
        model = Transaction
        fields = [
            "transaction_type",
            "purchase_category",
            "expense_category",
            "cashbalance_category",
            "amount",
            "description",
            "created_on",
        ]

        widgets = {
            "transaction_type": forms.Select(
                attrs={"class": "form-input w-full border-2 rounded-lg p-2"}
            ),

            "purchase_category": forms.Select(
                attrs={"class": "form-input w-full border-2 rounded-lg p-2"}
            ),

            "expense_category": forms.Select(
                attrs={"class": "form-input w-full border-2 rounded-lg p-2"}
            ),

            "cashbalance_category": forms.Select(
                attrs={"class": "form-input w-full border-2 rounded-lg p-2"}
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-input w-full border-2 rounded-lg p-2",
                    "placeholder": "Enter Amount"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-input w-full border-2 rounded-lg p-2",
                    "rows": 2
                }
            ),

            "created_on": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-input w-full border-2 rounded-lg p-2"
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        tx_type = cleaned_data.get("transaction_type")

        purchase = cleaned_data.get("purchase_category")
        expense = cleaned_data.get("expense_category")
        cashbalance = cleaned_data.get("cashbalance_category")

        # Clear unused fields
        if tx_type != "PURCHASE":
            cleaned_data["purchase_category"] = None
        if tx_type != "EXPENSE":
            cleaned_data["expense_category"] = None
        if tx_type != "CASHBALANCE":
            cleaned_data["cashbalance_category"] = None

        # Enforce required category
        if tx_type == "PURCHASE" and not purchase:
            self.add_error("purchase_category", "Purchase category is required")

        if tx_type == "EXPENSE" and not expense:
            self.add_error("expense_category", "Expense category is required")

        if tx_type == "CASHBALANCE" and not cashbalance:
            self.add_error("cashbalance_category", "Cash balance category is required")

        return cleaned_data

    
