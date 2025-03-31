from django.urls import path
from . import views

urlpatterns = [
    path('register-user/', views.register_user, name='register_user'),
    path('apply-loan/', views.apply_loan, name='apply_loan'),
    path('make-payment/', views.make_payment, name='make_payment'),
    path('get-statement/', views.get_statement, name='get_statement')
]