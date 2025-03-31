from django.db import models
import uuid
class User(models.Model):
    unique_user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    aadhar_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    email_id = models.EmailField(unique=True)
    annual_income = models.DecimalField(max_digits=15, decimal_places=2)
    credit_score = models.IntegerField(null=True, blank=True)

class Loan(models.Model):
    loan_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=50)
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_period = models.IntegerField()
    disbursement_date = models.DateField()

class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField()
class Billing(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    billing_date = models.DateField()
    due_date = models.DateField()
    min_due = models.DecimalField(max_digits=15, decimal_places=2)
    principal_balance = models.DecimalField(max_digits=15, decimal_places=2)
    
class DuePayment(models.Model):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE)
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=15, decimal_places=2)