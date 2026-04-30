import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.merchants.models import Merchant, LedgerEntry, BankAccount
from apps.payouts.models import Payout
import uuid
import random
from datetime import datetime, timedelta

# Clear existing data
Merchant.objects.all().delete()

# More realistic merchant data
MERCHANTS_DATA = [
    {
        "name": "TechStartup Inc",
        "email": "finance@techstartup.com",
        "initial_balance": 500000,  # ₹5,000
        "transactions": 8
    },
    {
        "name": "E-Commerce Hub",
        "email": "payments@ecomhub.com",
        "initial_balance": 1500000,  # ₹15,000
        "transactions": 12
    },
    {
        "name": "SaaS Solutions",
        "email": "accounting@saasolutions.com",
        "initial_balance": 2500000,  # ₹25,000
        "transactions": 15
    },
    {
        "name": "Digital Agency",
        "email": "billing@digitalagency.com",
        "initial_balance": 750000,  # ₹7,500
        "transactions": 6
    },
]

# Bank details for realistic data
BANK_DETAILS = [
    {"account_holder": "TechStartup Inc", "ifsc": "HDFC0000001"},
    {"account_holder": "E-Commerce Hub Ltd", "ifsc": "ICIC0000001"},
    {"account_holder": "SaaS Solutions Pvt", "ifsc": "AXIS0000001"},
    {"account_holder": "Digital Agency Co", "ifsc": "SBIN0000001"},
]

merchants = []
print("🌱 Seeding database with dynamic merchant data...\n")

for idx, merchant_data in enumerate(MERCHANTS_DATA, 1):
    # Create merchant
    merchant = Merchant.objects.create(
        name=merchant_data["name"],
        email=merchant_data["email"]
    )
    merchants.append(merchant)
    
    # Create bank account
    bank_info = BANK_DETAILS[idx - 1]
    BankAccount.objects.create(
        merchant=merchant,
        account_number=f"{''.join([str(random.randint(0,9)) for _ in range(12)])}",
        ifsc_code=bank_info["ifsc"],
        account_holder_name=bank_info["account_holder"],
        is_active=True
    )
    
    # Add secondary bank account
    BankAccount.objects.create(
        merchant=merchant,
        account_number=f"{''.join([str(random.randint(0,9)) for _ in range(12)])}",
        ifsc_code=bank_info["ifsc"],
        account_holder_name=bank_info["account_holder"],
        is_active=False  # Inactive account
    )
    
    # Create initial ledger entries (credits)
    initial_balance = merchant_data["initial_balance"]
    num_transactions = merchant_data["transactions"]
    
    # Distribute balance across transactions
    transaction_amounts = []
    remaining = initial_balance
    for t in range(num_transactions - 1):
        amount = random.randint(50000, 300000)  # 500 to 3000 paise
        transaction_amounts.append(amount)
        remaining -= amount
    transaction_amounts.append(max(50000, remaining))  # Last transaction gets remainder
    
    # Create ledger entries with realistic timing
    now = datetime.now()
    for t_idx, amount in enumerate(transaction_amounts):
        # Spread transactions over last 30 days
        days_ago = random.randint(0, 30)
        created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        entry = LedgerEntry.objects.create(
            merchant=merchant,
            entry_type='credit',
            amount_paise=amount,
            description=f'Payment from customer {random.randint(100, 999)}'
        )
        entry.created_at = created_at
        entry.save(update_fields=['created_at'])
    
    print(f"✅ {merchant.name}")
    print(f"   💰 Initial Balance: ₹{initial_balance / 100:,.2f}")
    print(f"   📊 Transactions: {num_transactions}")
    print(f"   🏦 Bank Accounts: 2 (1 active, 1 inactive)")
    print()

print(f"\n✨ Successfully seeded {len(merchants)} merchants with dynamic data!")
