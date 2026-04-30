import uuid
from django.db import models

class Merchant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='bank_accounts')
    account_number = models.CharField(max_length=64)
    ifsc_code = models.CharField(max_length=32)
    account_holder_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.account_holder_name} - {self.account_number}"

class LedgerEntry(models.Model):
    ENTRY_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='ledger_entries')
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES)
    amount_paise = models.BigIntegerField()
    # payout is nullable; credits could be from refunds referencing payout
    payout = models.ForeignKey('payouts.Payout', null=True, blank=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.entry_type} {self.amount_paise} for {self.merchant_id}"
