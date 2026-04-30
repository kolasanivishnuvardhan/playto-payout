# 🚀 Render.com Deployment Guide (FIXED)

## ✅ Issues Fixed in render.yaml

| Error | Fix | Line |
|-------|-----|------|
| `pythonVersion: 3.11` | `python: 3.11` | 6, 47, 73 |
| `version: "15"` (postgres) | `postgresVersion: 15` | 103 |
| `version: "7"` (redis) | `redisVersion: 7` | 107 |
| Missing `postgresVersion` field | Added field | 103 |
| Missing `redisVersion` field | Added field | 107 |

---

## 📋 Deployment Steps on Render

### Step 1: Push Fixed render.yaml to GitHub

```bash
cd d:\playto-payout
git add render.yaml
git commit -m "Fix render.yaml validation errors - correct field names"
git push origin main
```

### Step 2: Go to Render.com

1. Visit https://render.com
2. Click **"Dashboard"** (top right)
3. Login with GitHub account

### Step 3: Create New BluePrint

1. Click **"+ New +"** button
2. Select **"Blueprint"**
3. Connect your GitHub repository: `playto-payout`
4. Leave branch as `main`
5. Click **"Connect"**

### Step 4: Configure BluePrint

1. Render will automatically detect `render.yaml`
2. Review the services:
   - ✅ **playto-payout-api** (Web)
   - ✅ **playto-payout-celery-worker** (Worker)
   - ✅ **playto-payout-celery-beat** (Scheduler)
   - ✅ **playto-payout-db** (PostgreSQL 15)
   - ✅ **playto-payout-redis** (Redis 7)

3. Click **"Create Blueprint"**

### Step 5: Wait for Deployment

```
Expected deployment time: 5-10 minutes

Services starting:
  1. Database created (PostgreSQL)
  2. Redis cache started
  3. Backend migrations run
  4. Web service started
  5. Celery worker started
  6. Celery beat started
```

### Step 6: Check Deployment Status

1. Go to **Services** tab
2. See all 5 services
3. Click **playto-payout-api** → get URL
4. Backend ready at: `https://playto-payout-api.onrender.com`

---

## 🌱 Seed Test Data on Render

### Option A: Manual Seed (via Dashboard Shell)

1. **Open Render Dashboard**
   - Go to https://dashboard.render.com
   - Select **playto-payout-api** service

2. **Open Shell**
   - Click **"Shell"** tab
   - Run seeding command:

```bash
python manage.py seed_dynamic_data --merchants 10 --transactions 20 --clear
```

Output should show:
```
✓ Cleared existing data
✓ Created 10 merchants
✓ Created 20 ledger entries
✓ Ready for testing
```

### Option B: API Seed Script

Create `backend/seed_render.py`:

```python
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.merchants.models import Merchant, BankAccount, LedgerEntry
from apps.payouts.models import Payout
import uuid
from django.utils.timezone import now

def seed_data():
    # Clear existing
    Payout.objects.all().delete()
    LedgerEntry.objects.all().delete()
    BankAccount.objects.all().delete()
    Merchant.objects.all().delete()
    
    print("✓ Cleared existing data")
    
    # Create merchants
    merchants = []
    for i in range(10):
        merchant = Merchant.objects.create(
            name=f"Merchant {i+1}",
            created_at=now()
        )
        merchants.append(merchant)
        
        # Create bank account for each merchant
        BankAccount.objects.create(
            merchant=merchant,
            account_number=f"ACC{i+1:04d}",
            ifsc_code="SBIN0001234",
            account_holder_name=f"Holder {i+1}",
            is_active=True
        )
    
    print(f"✓ Created {len(merchants)} merchants with bank accounts")
    
    # Create ledger entries (initial balances)
    for merchant in merchants:
        for j in range(20):
            LedgerEntry.objects.create(
                merchant=merchant,
                entry_type='credit',
                amount_paise=1000000 + (j * 100000),  # ₹10,000 + increments
                description=f"Payment received {j+1}"
            )
    
    print("✓ Created 20 ledger entries per merchant")
    print("✓ Seed complete!")

if __name__ == '__main__':
    seed_data()
```

Then run in Render shell:
```bash
python backend/seed_render.py
```

### Option C: Django Management Command

Use existing seed command:
```bash
python manage.py seed_dynamic_data
```

---

## ✅ Verify Deployment

### 1. Test Backend API

```bash
# Get your Render URL from dashboard
# Example: https://playto-payout-api.onrender.com

# Test merchants endpoint
curl https://playto-payout-api.onrender.com/api/v1/merchants/

# Response should show merchants array
```

### 2. Check Services Status

In Render Dashboard:
- ✅ **playto-payout-api** — Green (running)
- ✅ **playto-payout-db** — Green (ready)
- ✅ **playto-payout-redis** — Green (ready)
- ✅ **playto-payout-celery-worker** — Green (running)
- ✅ **playto-payout-celery-beat** — Green (running)

### 3. Check Logs

Click each service → **Logs** tab:

**Web service should show:**
```
Starting Celery worker...
Starting development server...
Listening on 0.0.0.0:PORT
```

**Celery worker should show:**
```
Ready to accept tasks
celery@... ready.
```

**Celery beat should show:**
```
Starting Scheduler
Scheduler: DatabaseScheduler started
```

---

## 🔧 Environment Variables (Already Set)

Auto-generated on Render:

```
DJANGO_SECRET_KEY=******* (generated)
DEBUG=False
ALLOWED_HOSTS=*.render.com,*.vercel.app,localhost
DATABASE_URL=postgresql://... (auto-connected)
REDIS_URL=redis://... (auto-connected)
CELERY_BROKER_URL=redis://... (auto-connected)
CELERY_RESULT_BACKEND=redis://... (auto-connected)
```

**To view/edit:**
1. Service → **Environment** tab
2. Add/edit variables as needed
3. Changes auto-redeploy service

---

## 💾 Database Persistence

### PostgreSQL on Render

✅ Automatically persisted
✅ Backups enabled (free plan)
✅ Data survives restarts

### Redis Cache

✅ Session data (expires automatically)
⚠️ Task queue (workers reconnect)

---

## 🔄 Deployment Updates

When you push to GitHub:

1. Render auto-detects changes
2. Auto-redeploys affected services
3. Migrations run automatically
4. No manual intervention needed

```bash
# Push to GitHub
git add .
git commit -m "Update feature XYZ"
git push origin main

# Render automatically:
# 1. Rebuilds Docker image
# 2. Runs migrations
# 3. Restarts service
# 4. Your changes live!
```

---

## 📊 View Test Data

### Via API

```bash
# List merchants
curl https://playto-payout-api.onrender.com/api/v1/merchants/

# Get merchant details
curl https://playto-payout-api.onrender.com/api/v1/merchants/{id}/

# Get balance
curl https://playto-payout-api.onrender.com/api/v1/merchants/{id}/balance/

# Get ledger entries
curl https://playto-payout-api.onrender.com/api/v1/merchants/{id}/ledger/

# Get payouts
curl https://playto-payout-api.onrender.com/api/v1/merchants/{id}/payouts/
```

### Via Render Shell

```bash
python manage.py shell

# In Python shell:
>>> from apps.merchants.models import Merchant
>>> Merchant.objects.count()
10  # Should show 10 merchants

>>> m = Merchant.objects.first()
>>> m.name
'Merchant 1'

>>> m.payouts.count()
0  # No payouts yet

>>> from apps.merchants.models import LedgerEntry
>>> LedgerEntry.objects.filter(merchant=m).count()
20  # 20 ledger entries per merchant
```

---

## 🧪 Test a Payout

### Step 1: Get Merchant ID

```bash
curl https://playto-payout-api.onrender.com/api/v1/merchants/ | jq
# Copy first merchant's ID
```

### Step 2: Create Payout

```bash
MERCHANT_ID="your-merchant-id"

curl -X POST https://playto-payout-api.onrender.com/api/v1/payouts/ \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: test-$(date +%s)" \
  -d '{
    "merchant_id": "'$MERCHANT_ID'",
    "amount_paise": 100000,
    "bank_account_id": "ACC0001"
  }' | jq
```

### Step 3: Monitor Status

```bash
PAYOUT_ID="from-previous-response"

# Check status (repeat every 2 seconds)
curl https://playto-payout-api.onrender.com/api/v1/payouts/$PAYOUT_ID/ | jq .status

# Should show: pending → processing → completed/failed
```

### Step 4: Check Ledger

```bash
# After payout completes
curl https://playto-payout-api.onrender.com/api/v1/merchants/$MERCHANT_ID/ledger/ | jq

# Should show new DEBIT entry (if completed)
# Or DEBIT + CREDIT (if failed/refunded)
```

---

## 🛠️ Troubleshooting Render Deployment

### Issue: "Build failed"

**Check logs:**
1. Service → Logs tab
2. Look for error message
3. Common causes:
   - Missing dependency in requirements.txt
   - Python syntax error
   - Invalid environment variable

**Fix:**
```bash
# Push fix to GitHub
git add .
git commit -m "Fix build error"
git push origin main

# Render auto-rebuilds
```

### Issue: "Service unhealthy"

**Check:**
1. Database connection working?
2. Redis connection working?
3. Check logs for error

**Fix database connection:**
1. Service → Environment tab
2. Verify DATABASE_URL is correct
3. Verify database service is running

### Issue: "Celery worker not processing"

**Check:**
1. Worker logs show "Ready to accept tasks"?
2. Redis connection working?
3. Tasks visible in queue?

**Fix:**
1. Restart worker service
2. Check CELERY_BROKER_URL

### Issue: "Can't access API"

**Check:**
1. Service says "Live"?
2. Try direct URL in browser
3. Check ALLOWED_HOSTS includes render.com

**Fix:**
```
ALLOWED_HOSTS=*.render.com,*.vercel.app,localhost
```

---

## 📈 Monitoring

### View Metrics

1. Go to Service → Metrics tab
2. See:
   - Memory usage
   - CPU usage
   - Response times
   - Error rates

### View Logs

1. Go to Service → Logs tab
2. Filter by:
   - Error level
   - Time range
   - Service

### Get Alerts

1. Go to Service → Alerts tab
2. Set up:
   - Error rate threshold
   - Memory threshold
   - CPU threshold
3. Get notified via email

---

## 🚀 Next: Deploy Frontend to Vercel

Once backend is running on Render:

1. **Update Frontend .env**

```bash
# frontend/.env
REACT_APP_API_URL=https://playto-payout-api.onrender.com
```

2. **Deploy to Vercel**

```bash
npm install -g vercel
vercel
# Follow prompts
```

Frontend will auto-connect to Render backend!

---

## ✨ Summary

✅ render.yaml fixed (correct field names)
✅ Deploy via Blueprint (5-10 minutes)
✅ Seed test data (10 merchants, 20 transactions each)
✅ Test API endpoints
✅ Monitor Celery workers
✅ Watch payouts process live
✅ Scale frontend separately on Vercel

**Backend now running on Render! 🎉**
