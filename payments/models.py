from decimal import Decimal
from django.db import models
from django.conf import settings

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def deposit(self, amount: Decimal):
        self.balance += amount
        self.save(update_fields=['balance'])

    def withdraw(self, amount: Decimal):
        if self.balance < amount:
            raise ValueError('Insufficient funds')
        self.balance -= amount
        self.save(update_fields=['balance'])

class Transaction(models.Model):
    TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('PAYOUT', 'Payout'),
        ('PROMO_SPEND', 'Promo Spend'),
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    ttype = models.CharField(max_length=20, choices=TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=200, blank=True)