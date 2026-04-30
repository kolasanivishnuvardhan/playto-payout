# Seed Test Data Guide

## 🌱 What is Seeding?

Seeding creates initial test data in your database so you can immediately test the payout system without manually creating merchants and transactions.

---

## 🎯 Quick Seed (Local Development)

### Seed with Default Data

```bash
cd d:\playto-payout
docker-compose exec -T backend python manage.py seed_dynamic_data
```

This creates:
- 10 merchants
- 20 transactions per merchant
- 200 total ledger entries
- Ready to test payouts immediately

### Seed with Custom Amounts

```bash
python manage.py seed_dynamic_data --merchants 50 --transactions 25
```

This creates:
- 50 merchants
- 25 transactions each (1250 total)
- More realistic data set

### Clear and Reseed

```bash
python manage.py seed_dynamic_data --merchants 10 --transactions 20 --clear
```

- `--clear` removes all existing data first
- Useful for starting fresh

---

## 🌐 Seed on Render (Production)

### Method 1: Via Render Shell (Recommended)

1. Go to Render dashboard
2. Click Web Service: **playto-payout-api**
3. Click **"Shell"** tab at top
4. Run command:

```bash
cd backend
python manage.py seed_dynamic_data --merchants 10 --transactions 20
```

5. Wait for completion
6. See: `✅ Successfully seeded X merchants`

### Method 2: Via SSH (Advanced)

```bash
# Get Render instance ID from logs
# SSH into instance
ssh render-instance

# Navigate to app
cd /app

# Run seed command
python backend/manage.py seed_dynamic_data --merchants 50 --transactions 25
```

### Method 3: Create Via API (Manual)

```bash
# Get your Render API URL
BACKEND_URL="https://playto-payout-api-xxx.onrender.com"

# Create merchant
curl -X POST $BACKEND_URL/api/v1/merchants/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Merchant Inc"}'

# Add credit to merchant (via Django shell)
# See next section
```

---

## 💾 What Data Gets Created?

### Merchants

Each merchant gets:
- Unique ID (UUID)
- Name (e.g., "Test Merchant 1", "Test Company A")
- Created timestamp
- Bank accounts (1-3 per merchant)

### Bank Accounts

Each merchant has:
- Account number (simulated)
- IFSC code (simulated)
- Account holder name
- Active status

### Ledger Entries (Credits)

Each transaction creates:
- Credit entry (money in)
- Amount: Random ₹1,000 - ₹50,000
- Description: "Payment received"
- Timestamp

### Example Seeded State

```
Merchant: "TechStartup Inc"
  Bank Accounts:
    - ACC-001234 (SBIN0001234) - Active
    - ACC-005678 (HDFC0005678) - Active
  
  Ledger Balance: ₹250,000 (from 5 transactions)
  Held Balance: ₹0 (no pending payouts)
  Available: ₹250,000 (ready to payout)
```

---

## 🧪 Testing After Seeding

### 1. Verify Data in Database

```bash
# Connect to database
docker-compose exec db psql -U postgres -d playto_payout

# Check merchants
SELECT COUNT(*) FROM merchants_merchant;
# Should show: 10 (or your specified amount)

# Check ledger entries
SELECT COUNT(*) FROM merchants_ledgerentry;
# Should show: 20 (or 10 * specified transactions)

# Check balance
SELECT 
  merchant_id, 
  SUM(CASE WHEN entry_type='credit' THEN amount_paise ELSE -amount_paise END) as balance
FROM merchants_ledgerentry
GROUP BY merchant_id
LIMIT 5;
```

### 2. Verify via API

```bash
# Get merchants
curl http://localhost:8000/api/v1/merchants/ | jq

# Get first merchant ID
MERCHANT_ID=$(curl -s http://localhost:8000/api/v1/merchants/ | jq -r '.[0].id')

# Get merchant balance
curl http://localhost:8000/api/v1/merchants/$MERCHANT_ID/balance/ | jq

# Expected output:
{
  "ledger_balance": 250000,      # ₹2500
  "held_balance": 0,              # Nothing pending
  "available_balance": 250000     # Ready to spend
}
```

### 3. Test Payout Creation

```bash
# Create test payout
MERCHANT_ID="<from-step-above>"

curl -X POST http://localhost:8000/api/v1/payouts/ \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: test-$(date +%s)" \
  -d '{
    "merchant_id": "'$MERCHANT_ID'",
    "amount_paise": 50000,
    "bank_account_id": "ACC-001234"
  }' | jq

# Response should be:
{
  "id": "payout-uuid",
  "status": "pending",
  "amount_paise": 50000,
  "created_at": "2026-04-30T..."
}
```

### 4. Watch Payout Process

```bash
# Watch status change
PAYOUT_ID="<from-step-above>"

for i in {1..10}; do
  STATUS=$(curl -s http://localhost:8000/api/v1/payouts/$PAYOUT_ID/ | jq -r '.status')
  echo "[$i] Status: $STATUS"
  sleep 1
done

# Expected timeline:
# [1] Status: pending
# [2] Status: pending
# [3] Status: processing
# [4] Status: processing
# [5] Status: completed (or failed, or still processing if hung)
```

### 5. Check Dashboard

1. Open http://localhost:3000
2. Select seeded merchant from dropdown
3. See balance: ₹2500 (or your seeded amount)
4. Try creating payout: 500 (₹5)
5. Watch status change in real-time
6. See balance update after completion

---

## 📋 Seed Commands Reference

### Production (Render)

```bash
# Basic seed (10 merchants, 20 transactions each)
python backend/manage.py seed_dynamic_data

# Large dataset (100 merchants, 50 transactions each)
python backend/manage.py seed_dynamic_data --merchants 100 --transactions 50

# Clear and reseed
python backend/manage.py seed_dynamic_data --merchants 10 --transactions 20 --clear

# Verify seed
python backend/manage.py shell
>>> from apps.merchants.models import Merchant
>>> Merchant.objects.count()
10
```

### Local (Docker)

```bash
# Seed in Docker
docker-compose exec -T backend python manage.py seed_dynamic_data

# With options
docker-compose exec -T backend python manage.py seed_dynamic_data --merchants 50 --transactions 25

# Full reset
docker-compose exec -T backend python manage.py seed_dynamic_data --clear
docker-compose exec -T backend python manage.py migrate
```

---

## 🔍 Understanding Seed Data

### Amount Distribution

Transactions are seeded with random amounts:
```
Minimum: ₹1,000 (100,000 paise)
Maximum: ₹50,000 (5,000,000 paise)
Distribution: Uniform random
```

### Merchant Names

Auto-generated names:
```
"Test Merchant 1"
"Test Merchant 2"
"Acme Corporation"
"TechStartup Inc"
"E-Commerce Ltd"
...
```

### Timestamps

All transactions dated:
```
1 week ago → now
Random times throughout the week
Realistic distribution
```

---

## ⚠️ Important Notes

### Seeding Overwrites Data

```bash
# WARNING: This creates new data
python manage.py seed_dynamic_data

# Result: Existing data is KEPT
# New merchants/transactions are ADDED

# To clear first:
python manage.py seed_dynamic_data --clear
```

### Idempotency Key

Each merchant's bank account is unique by:
- Merchant ID
- Account number

So seeding is safe to run multiple times (won't create duplicates).

### Ledger is Immutable

Once seeded, ledger entries can't be deleted:
```
✅ Can create new merchants
✅ Can create new transactions
❌ Can't delete existing ledger entries
```

This is intentional (audit trail protection).

---

## 📊 Seed Data Size Estimates

| Merchants | Transactions | Total Entries | DB Size |
|-----------|--------------|---------------|---------|
| 10 | 20 | 200 | ~2 MB |
| 50 | 25 | 1,250 | ~8 MB |
| 100 | 50 | 5,000 | ~25 MB |
| 1,000 | 100 | 100,000 | ~400 MB |

Render free tier database: 1 GB limit
→ Can seed up to ~500,000 entries

---

## 🚀 Post-Seed Testing Checklist

- [ ] Verify merchant count in database
- [ ] Check ledger entries created
- [ ] Test API: GET /merchants/
- [ ] Test API: GET /merchants/{id}/balance/
- [ ] Create test payout via API
- [ ] Verify payout processes (2-3 seconds)
- [ ] Check ledger entry created
- [ ] Test dashboard: Select seeded merchant
- [ ] Test dashboard: Create payout
- [ ] Watch status change: pending → processing → completed
- [ ] Verify balance updated
- [ ] Check ledger entry visible
- [ ] Celebrate! 🎉

---

## 🆘 Troubleshooting

### Seed Fails: "No module named 'seed'"

```bash
# Make sure you're in backend directory
cd backend
python manage.py seed_dynamic_data

# Or from root:
python backend/manage.py seed_dynamic_data
```

### Seed Fails: "Database connection error"

```bash
# Ensure database is running
docker-compose ps

# Should show: db (postgres) - Up

# If not running:
docker-compose up -d db
```

### Data Not Showing in Dashboard

```bash
# 1. Check browser cache
# Ctrl+Shift+Delete → Clear all

# 2. Hard refresh
# Ctrl+Shift+R

# 3. Check merchant list
curl http://localhost:8000/api/v1/merchants/

# If empty, reseed:
python manage.py seed_dynamic_data --clear
```

### "Insufficient funds" when creating payout

```bash
# Expected behavior if you didn't seed with --clear
# Or if balance was spent on previous payouts

# Solution: Reseed with more merchants
python manage.py seed_dynamic_data --merchants 100 --transactions 50

# Or seed specific merchant with huge balance
# Via Django shell:
>>> from apps.merchants.models import Merchant, LedgerEntry
>>> m = Merchant.objects.first()
>>> LedgerEntry.objects.create(
...   merchant=m,
...   entry_type='credit',
...   amount_paise=100000000  # ₹10,00,000
... )
```

---

## 📚 Next Steps

1. ✅ Seed data on Render
2. → Test payouts in dashboard
3. → Monitor Celery workers
4. → Check ledger entries
5. → Celebrate deployment! 🎉

---

**Ready to seed? Run the appropriate command for your environment!**
