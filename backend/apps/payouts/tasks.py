import random
import time
from celery import shared_task
from django.db import transaction
from django.utils.timezone import now
from datetime import timedelta
from .models import Payout
from apps.merchants.models import LedgerEntry
from .state_machine import transition_payout


def simulate_bank_settlement():
    r = random.random()
    if r < 0.70:
        return 'success'
    elif r < 0.90:
        return 'failure'
    else:
        time.sleep(5)
        return 'hang'


@shared_task(bind=True, max_retries=3)
def process_payout(self, payout_id):
    with transaction.atomic():
        try:
            payout = Payout.objects.select_for_update().get(id=payout_id)
        except Payout.DoesNotExist:
            return

        if payout.status != 'pending':
            return

        payout.status = 'processing'
        payout.attempt_count += 1
        payout.last_attempted_at = now()
        payout.save(update_fields=['status', 'attempt_count', 'last_attempted_at'])

    outcome = simulate_bank_settlement()

    with transaction.atomic():
        payout = Payout.objects.select_for_update().get(id=payout_id)

        if payout.status != 'processing':
            return

        if outcome == 'success':
            payout.status = 'completed'
            payout.save(update_fields=['status', 'updated_at'])
            LedgerEntry.objects.create(
                merchant_id=payout.merchant_id,
                entry_type='debit',
                amount_paise=payout.amount_paise,
                payout=payout,
                description=f'Payout {payout.id} completed'
            )

        elif outcome == 'failure':
            payout.status = 'failed'
            payout.save(update_fields=['status', 'updated_at'])
            LedgerEntry.objects.create(
                merchant_id=payout.merchant_id,
                entry_type='credit',
                amount_paise=payout.amount_paise,
                payout=payout,
                description=f'Refund for failed payout {payout.id}'
            )


@shared_task
def retry_stuck_payouts():
    cutoff = now() - timedelta(seconds=30)
    stuck = Payout.objects.filter(
        status='processing',
        last_attempted_at__lt=cutoff,
        attempt_count__lt=3
    )
    for payout in stuck:
        process_payout.apply_async(
            args=[str(payout.id)],
            countdown=2 ** payout.attempt_count
        )

    exhausted = Payout.objects.filter(
        status='processing',
        last_attempted_at__lt=cutoff,
        attempt_count__gte=3
    )
    for payout in exhausted:
        transition_payout(str(payout.id), 'failed')
