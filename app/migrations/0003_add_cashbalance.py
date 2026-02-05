# Generated migration to add CashBalance functionality

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_transaction_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashBalanceCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='transaction',
            name='cashbalance_category',
            field=models.CharField(blank=True, choices=[('OPENING', 'Opening Balance'), ('CLOSING', 'Closing Balance'), ('OTHER', 'Other')], max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('SALE', 'Sales'), ('PURCHASE', 'Purchase'), ('EXPENSE', 'Expense'), ('CASHBALANCE', 'Cash Balance')], max_length=12),
        ),
    ]
