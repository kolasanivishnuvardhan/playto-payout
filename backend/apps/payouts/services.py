from django.db import transaction, IntegrityError
from django.db.models import Sum, F, Case, When, BigIntegerField
from django.db.models.functions import Coalesce
from apps.merchants.models import Merchant, LedgerEntry
from .models import Payout

class InsufficientFundsError(Exception):
    pass


def create_payout(merchant_id, amount_paise, bank_account_id, idempotency_key):
    # Step 2: Lock the merchant row and check balance atomically
    with transaction.atomic():
        merchant = Merchant.objects.select_for_update().get(id=merchant_id)

        ledger_balance = LedgerEntry.objects.filter(
            merchant_id=merchant_id
        ).aggregate(
            balance=Coalesce(Sum(
                Case(
                    When(entry_type='credit', then=F('amount_paise')),
                    When(entry_type='debit', then=-F('amount_paise')),
                    output_field=BigIntegerField()
                )
            ), 0, output_field=BigIntegerField())
        )['balance']

        held_balance = Payout.objects.filter(
            merchant_id=merchant_id,
            status__in=['pending', 'processing']
        ).aggregate(
            held=Coalesce(Sum('amount_paise'), 0, output_field=BigIntegerField())
        )['held']

        available = ledger_balance - held_balance

        if available < amount_paise:
            raise InsufficientFundsError(f"Available: {available}, Requested: {amount_paise}")

        payout = Payout.objects.create(
            merchant_id=merchant_id,
            amount_paise=amount_paise,
            bank_account_id=bank_account_id,
            idempotency_key=idempotency_key,
            status='pending'
        )

        return payout, True


def create_payout_idempotent(merchant_id, amount_paise, bank_account_id, idempotency_key):
    # Fast path
    try:
        existing = Payout.objects.get(merchant_id=merchant_id, idempotency_key=idempotency_key)
        return existing, False
    except Payout.DoesNotExist:
        pass

    try:
        payout, created = create_payout(merchant_id, amount_paise, bank_account_id, idempotency_key)
        return payout, created
    except IntegrityError:
        existing = Payout.objects.get(merchant_id=merchant_id, idempotency_key=idempotency_key)
        return existing, False
