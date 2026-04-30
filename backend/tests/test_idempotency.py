from django.test import TransactionTestCase
from apps.merchants.models import Merchant, LedgerEntry
from apps.payouts.models import Payout
from apps.payouts.services import create_payout_idempotent


class IdempotencyTest(TransactionTestCase):
    def setUp(self):
        self.merchant1 = Merchant.objects.create(name="Merchant 1", email="m1@t.com")
        self.merchant2 = Merchant.objects.create(name="Merchant 2", email="m2@t.com")
        for m in [self.merchant1, self.merchant2]:
            LedgerEntry.objects.create(
                merchant=m,
                entry_type='credit',
                amount_paise=50000,
                description='Seed'
            )

    def test_same_key_returns_same_payout(self):
        """Calling create_payout_idempotent twice with same key returns same payout"""
        payout1, created1 = create_payout_idempotent(
            merchant_id=self.merchant1.id,
            amount_paise=5000,
            bank_account_id='ACC001',
            idempotency_key='unique-key-123'
        )
        payout2, created2 = create_payout_idempotent(
            merchant_id=self.merchant1.id,
            amount_paise=5000,
            bank_account_id='ACC001',
            idempotency_key='unique-key-123'
        )
        self.assertEqual(payout1.id, payout2.id)
        self.assertTrue(created1)
        self.assertFalse(created2)
        self.assertEqual(Payout.objects.filter(merchant=self.merchant1).count(), 1)

    def test_different_merchants_same_key_creates_two_payouts(self):
        """Same idempotency_key for two merchants creates two separate payouts"""
        payout1, _ = create_payout_idempotent(
            merchant_id=self.merchant1.id,
            amount_paise=5000,
            bank_account_id='ACC001',
            idempotency_key='shared-key'
        )
        payout2, _ = create_payout_idempotent(
            merchant_id=self.merchant2.id,
            amount_paise=5000,
            bank_account_id='ACC002',
            idempotency_key='shared-key'
        )
        self.assertNotEqual(payout1.id, payout2.id)
        self.assertEqual(Payout.objects.count(), 2)
