from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Loan, Payment
from .tasks import calculate_credit_score
from datetime import timedelta, date
from decimal import Decimal

@api_view(['POST'])
def register_user(request):
    aadhar_id = request.data.get('aadhar_id')
    name = request.data.get('name')
    email_id = request.data.get('email_id')
    annual_income = request.data.get('annual_income')
    if User.objects.filter(email_id=email_id).exists():
        return Response({'error': 'Email already exists'}, status=400) # Returns a bad request if the email exists
    user = User.objects.create(aadhar_id=aadhar_id, name=name, email_id=email_id, annual_income=annual_income)
    calculate_credit_score.delay(user.unique_user_id,"transactions_data_backend__1_.csv")
    return Response({'unique_user_id': user.unique_user_id})

@api_view(['POST'])
def apply_loan(request):
    user_id = request.data.get('unique_user_id')
    loan_type = request.data.get('loan_type')
    loan_amount = request.data.get('loan_amount')
    interest_rate = request.data.get('interest_rate')
    term_period = request.data.get('term_period')
    disbursement_date = request.data.get('disbursement_date')
    user = User.objects.get(unique_user_id=user_id)
    if user.credit_score is None:
        return Response({'error': 'Credit score not available'}, status=400) # Added check for None
    if user.credit_score < 450:
        return Response({'error': 'Credit score too low'})
    if user.annual_income < 150000:
        return Response({'error': 'Annual income too low'})
    if loan_amount > 5000:
        return Response({'error': 'Loan amount exceeds limit'})
    if interest_rate < 12:
        return Response({'error': 'Interest rate too low'})
    monthly_income = user.annual_income / 12
    emi = Decimal(loan_amount) / term_period
    if emi > monthly_income * Decimal('0.20'):
        return Response({'error': 'EMI exceeds 20% of monthly income'})
    loan = Loan.objects.create(user=user, loan_type=loan_type, loan_amount=loan_amount, interest_rate=interest_rate, term_period=term_period, disbursement_date=disbursement_date, principal_balance=loan_amount)
    due_dates = []
    current_date = date.fromisoformat(disbursement_date)
    for _ in range(term_period):
        current_date += timedelta(days=30)
        due_dates.append({'date': current_date, 'amount_due': emi})
    return Response({'loan_id': loan.loan_id, 'due_dates': due_dates})

@api_view(['POST'])
def make_payment(request):
    loan_id = request.data.get('loan_id')
    amount = request.data.get('amount')
    loan = Loan.objects.get(loan_id=loan_id)
    Payment.objects.create(loan=loan, amount=amount, payment_date=date.today())
    loan.principal_balance -= Decimal(amount)
    loan.save()
    return Response({'message': 'Payment recorded'})

@api_view(['GET'])
def get_statement(request):
    loan_id = request.GET.get('loan_id')
    loan = Loan.objects.get(loan_id=loan_id)
    past_transactions = []
    for payment in Payment.objects.filter(loan=loan):
        past_transactions.append({
            'date': payment.payment_date,
            'principal': loan.loan_amount,
            'interest': loan.interest_rate,
            'amount_paid': payment.amount,
        })
    upcoming_transactions = []
    current_date = loan.disbursement_date
    emi = loan.loan_amount / loan.term_period
    for _ in range(loan.term_period):
        current_date += timedelta(days=30)
        upcoming_transactions.append({'date': current_date, 'amount_due': emi})
    return Response({'past_transactions': past_transactions, 'upcoming_transactions': upcoming_transactions})