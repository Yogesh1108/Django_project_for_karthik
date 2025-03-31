from celery import shared_task
import pandas as pd
from .models import User

def calculate_credit_score(user_id, csv_file_path):
    user = User.objects.get(unique_user_id=user_id)
    df = pd.read_csv("transactions_data_backend__1_.csv")
    user_data = df[df['AADHAR ID'] == user.aadhar_id]
    user_data['Amount'] = user_data.apply(lambda row: row['Amount'] if row['Transaction_type'] == "CREDIT" else -row['Amount'], axis=1)
    total_balance = user_data['Amount'].sum()
    if total_balance >= 1000000:
        credit_score = 900
    elif total_balance <= 10000:
        credit_score = 300
    else:
        credit_score = 300 + int((total_balance - 10000) / 15000) * 10
    user.credit_score = credit_score
    user.save()
    return credit_score
import logging
import pandas as pd
from celery import shared_task

logger = logging.getLogger(__name__)  # Get a logger for the module

@shared_task
def calculate_credit_score(user_id, csv_file_path):
    try:
        logger.info(f"Attempting to read CSV file: {"transactions_data_backend__1_.csv"}")
        df = pd.read_csv("transactions_data_backend__1_.csv")
        # ... rest of your code
    except FileNotFoundError:
        logger.error(f"CSV file not found: {"transactions_data_backend__1_.csv"}")
        # Handle the error appropriately
    except PermissionError as e:
        logger.error(f"Permission error accessing CSV: {"transactions_data_backend__1_.csv"}, Error: {e}")
        # Handle the error appropriately
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        # Handle other exceptions
        # your_app/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Loan, Billing, DuePayment

@shared_task
def initiate_billing():
    today = timezone.now().date()
    loans_to_bill = Loan.objects.filter(next_billing_date=today)

    for loan in loans_to_bill:
        # Calculate min_due
        principal_balance = loan.loan_amount  # Assuming initial loan amount is the principal for the first cycle
        daily_apr = round(loan.interest_rate / Decimal('365'), 3)
        apr_accrued = daily_apr * 30 * principal_balance  # Assuming 30 days in a billing cycle
        min_due = (principal_balance * Decimal('0.03')) + apr_accrued

        # Create Billing record
        billing = Billing.objects.create(
            loan=loan,
            billing_date=today,
            min_due=min_due,
            apr_accrued=apr_accrued
        )

        # Create DuePayment record
        due_date = today + timedelta(days=15)
        DuePayment.objects.create(
            billing=billing,
            due_date=due_date,
            amount_due=min_due
        )

        # Update next_billing_date
        loan.next_billing_date = today + timedelta(days=30)
        loan.save()