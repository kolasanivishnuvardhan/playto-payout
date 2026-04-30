import threading
from django.test import TransactionTestCase
from apps.merchants.models import Merchant, LedgerEntry
from apps.payouts.services import create_payout_idempotent, InsufficientFundsError


class ConcurrentPayoutTest(TransactionTestCase):
    def setUp(self):
        self.merchant = Merchant.objects.create(name="Test Merchant", email="t@t.com")
        LedgerEntry.objects.create(
            merchant=self.merchant,
            entry_type='credit',
            amount_paise=10000,
            description='Seed credit'
        )

    def test_concurrent_overdraw_prevention(self):
        """Two simultaneous 6000 paise requests — exactly one must succeed"""
        results = []
        errors = []

        def attempt_payout(key_suffix):
            try:
                payout, created = create_payout_idempotent(
                    merchant_id=self.merchant.id,
                    amount_paise=6000,
                    bank_account_id='ACC001',
                    idempotency_key=f'test-key-{key_suffix}'
                )
                results.append(('success', created))
            except InsufficientFundsError as e:
                errors.append(str(e))

        t1 = threading.Thread(target=attempt_payout, args=('1',))
        t2 = threading.Thread(target=attempt_payout, args=('2',))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual(len(results), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn('Available', errors[0])
