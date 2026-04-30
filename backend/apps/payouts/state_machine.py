from django.db import transaction
from django.utils.timezone import now
from .models import Payout
from apps.merchants.models import LedgerEntry

VALID_TRANSITIONS = {
    'pending': ['processing'],
    'processing': ['completed', 'failed'],
    'completed': [],
    'failed': [],
}

class InvalidStateTransitionError(Exception):
    pass


def transition_payout(payout_id, new_status):
    with transaction.atomic():
        payout = Payout.objects.select_for_update().get(id=payout_id)
        allowed = VALID_TRANSITIONS.get(payout.status, [])
        if new_status not in allowed:
            raise InvalidStateTransitionError(f"Cannot transition from {payout.status} to {new_status}")

        payout.status = new_status
        payout.updated_at = now()
        payout.save(update_fields=['status', 'updated_at'])

        if new_status == 'failed':
            LedgerEntry.objects.create(
                merchant_id=payout.merchant_id,
                entry_type='credit',
                amount_paise=payout.amount_paise,
                payout=payout,
                description=f'Refund for failed payout {payout.id}'
            )

        return payout
