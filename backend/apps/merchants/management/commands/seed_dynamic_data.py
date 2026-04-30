from django.core.management.base import BaseCommand
from django.db import transaction
from apps.merchants.models import Merchant, LedgerEntry, BankAccount
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Generate dynamic merchant data with random transactions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--merchants',
            type=int,
            default=5,
            help='Number of merchants to create'
        )
        parser.add_argument(
            '--transactions',
            type=int,
            default=10,
            help='Average transactions per merchant'
        )
        parser.add_argument(
            '--min-balance',
            type=int,
            default=100000,
            help='Minimum initial balance in paise'
        )
        parser.add_argument(
            '--max-balance',
            type=int,
            default=5000000,
            help='Maximum initial balance in paise'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            Merchant.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing data'))

        num_merchants = options['merchants']
        avg_transactions = options['transactions']
        min_balance = options['min_balance']
        max_balance = options['max_balance']

        merchants_created = 0
        total_ledger_entries = 0

        self.stdout.write(self.style.SUCCESS(f'\n🌱 Creating {num_merchants} merchants with dynamic data...\n'))

        for i in range(num_merchants):
            # Generate merchant data
            merchant_name = self._generate_company_name()
            email = merchant_name.lower().replace(' ', '_') + f'_{i}@playto.com'
            
            merchant = Merchant.objects.create(
                name=merchant_name,
                email=email
            )
            merchants_created += 1

            # Create 1-3 bank accounts
            num_accounts = random.randint(1, 3)
            for acc_idx in range(num_accounts):
                BankAccount.objects.create(
                    merchant=merchant,
                    account_number=self._generate_account_number(),
                    ifsc_code=self._generate_ifsc(),
                    account_holder_name=f"{merchant_name} Account {acc_idx + 1}",
                    is_active=(acc_idx == 0)  # Only first is active
                )

            # Generate random transactions
            initial_balance = random.randint(min_balance, max_balance)
            num_transactions = random.randint(max(1, avg_transactions - 5), avg_transactions + 5)
            
            transaction_amounts = self._distribute_balance(initial_balance, num_transactions)
            
            now = datetime.now()
            for t_idx, amount in enumerate(transaction_amounts):
                days_ago = random.randint(0, 60)
                hours_ago = random.randint(0, 23)
                created_at = now - timedelta(days=days_ago, hours=hours_ago)
                
                entry = LedgerEntry.objects.create(
                    merchant=merchant,
                    entry_type='credit',
                    amount_paise=amount,
                    description=self._generate_description()
                )
                entry.created_at = created_at
                entry.save(update_fields=['created_at'])
                total_ledger_entries += 1

            # Display merchant info
            self.stdout.write(
                f"✅ {merchant.name:25} | "
                f"Balance: ₹{initial_balance / 100:>10,.2f} | "
                f"Transactions: {num_transactions:2d}"
            )

        self.stdout.write(self.style.SUCCESS(
            f'\n✨ Successfully created {merchants_created} merchants '
            f'with {total_ledger_entries} ledger entries!\n'
        ))

    def _generate_company_name(self):
        """Generate random company name"""
        prefixes = [
            'Tech', 'Digital', 'Smart', 'Cloud', 'Data', 'Cyber',
            'Swift', 'Prime', 'Elite', 'Nexus', 'Apex', 'Volt',
            'Quantum', 'Fusion', 'Horizon', 'Stellar', 'Ascend', 'Innovate'
        ]
        suffixes = [
            'Solutions', 'Labs', 'Hub', 'Works', 'Systems',
            'Industries', 'Group', 'Corp', 'Ventures', 'Agency', 'Studio',
            'Innovations', 'Services', 'Technologies', 'Enterprises', 'Partners'
        ]
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"

    def _generate_account_number(self):
        """Generate random bank account number"""
        return ''.join([str(random.randint(0, 9)) for _ in range(14)])

    def _generate_ifsc(self):
        """Generate random IFSC code"""
        banks = ['HDFC', 'ICIC', 'AXIS', 'SBIN', 'UTIB', 'HSBC']
        return f"{random.choice(banks)}0{''.join([str(random.randint(0, 9)) for _ in range(6)])}"

    def _distribute_balance(self, total, num_transactions):
        """Distribute balance across transactions"""
        if num_transactions <= 0:
            return [total]
        
        amounts = []
        remaining = total
        for _ in range(num_transactions - 1):
            # Calculate max amount to ensure last transaction has at least 1000
            max_amount = max(10000, remaining - 10000)
            min_amount = 10000
            
            if max_amount < min_amount:
                # If remaining is too small, just take half
                amount = remaining // 2
            else:
                amount = random.randint(min_amount, min(max_amount, 500000))
            
            if amount <= 0:
                continue
                
            amounts.append(amount)
            remaining -= amount
        
        if remaining > 0:
            amounts.append(remaining)
        
        return amounts if amounts else [total]

    def _generate_description(self):
        """Generate random transaction description"""
        types = [
            'Payment from customer',
            'Refund received',
            'Settlement credit',
            'API transaction',
            'Marketplace payout',
            'Invoice payment',
            'Transfer received',
            'Batch deposit'
        ]
        customer_ids = [str(random.randint(1000, 9999)) for _ in range(5)]
        return f"{random.choice(types)} {random.choice(customer_ids)}"
