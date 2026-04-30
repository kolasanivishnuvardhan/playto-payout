# Playto Payout Engine

A production-grade asynchronous payout processing system built with Django, PostgreSQL, Redis, and Celery.

## ✨ Features

✅ **Asynchronous Processing** — Celery workers process payouts in background  
✅ **Idempotency** — Same request returns same payout (prevents duplicates)  
✅ **Concurrency Safe** — Database row-level locks prevent race conditions  
✅ **Real-Time Balance** — Calculated from immutable ledger entries  
✅ **Auto-Refunds** — Failed payouts automatically refund to merchant  
✅ **Retry Logic** — Exponential backoff for stuck payouts (max 3 attempts)  
✅ **Live Dashboard** — Real-time payout tracking with 5-second auto-refresh  
✅ **Ledger History** — Immutable transaction audit trail  
✅ **Production Ready** — Transaction-safe with comprehensive test coverage

## 🏗️ Architecture

```
Frontend (Port 3000)
    ↓
Backend API (Port 8000) ←→ PostgreSQL (Port 5432)
    ↓                       ↑
Celery Worker          Redis (Port 6379)
    ↓                       ↑
Celery Beat ←→ Message Queue
```

### Tech Stack

- **Backend:** Django 4.2, Django REST Framework
- **Database:** PostgreSQL 15 (UUID keys, BigInteger amounts)
- **Task Queue:** Celery 5.3 + Redis 7
- **Scheduler:** Celery Beat (60-second check interval)
- **Frontend:** Vanilla JavaScript + HTML5
- **Container:** Docker & Docker Compose

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose

### Installation

```bash
git clone <repo-url>
cd playto-payout

# Build and start all services
docker-compose up -d --build

# Run migrations
docker-compose exec -T backend python manage.py migrate

# Seed data (optional)
docker-compose exec -T backend python manage.py seed_dynamic_data
```

### Access

- **Dashboard:** http://localhost:3000
- **API:** http://localhost:8000/api/v1
- **Admin:** http://localhost:8000/admin

### Verify

```bash
# Check services
docker-compose ps

# Test API
curl http://localhost:8000/api/v1/merchants/

# View logs
docker-compose logs -f backend
docker-compose logs -f celery-worker
```

## 💡 How It Works

### Three Balance Types

1. **Ledger Balance** = Sum of all credits - Sum of all debits
   - Shows total money merchant has ever received

2. **Held Balance** = Sum of payouts in `pending` or `processing` status
   - Money locked in flight, prevents double-spending

3. **Available Balance** = Ledger Balance - Held Balance
   - What merchant can withdraw right now

### Payout Lifecycle

```
pending (T+0s)
    ↓
processing (T+1s)
    ├→ SUCCESS (70%) → completed ✅ (debit entry added)
    ├→ FAILURE (20%) → failed ❌ (auto-refunded)
    └→ HANG (10%) → auto-retry after 60s (exponential backoff)
```

### Key Guarantees

- **Atomicity** — Status change and ledger entry always happen together
- **Idempotency** — Duplicate requests with same key return same payout
- **No Overdraft** — Database lock prevents balance going negative
- **No Data Loss** — Ledger is immutable append-only log
- **Auto-Recovery** — Stuck payouts auto-retry with bounded attempts

## 📋 API Endpoints

### Create Payout

```bash
POST /api/v1/payouts/

{
  "amount_paise": 100000,      # ₹1000
  "bank_account_id": "acc-123",
  "idempotency_key": "unique-key"  # Required for idempotency
}

Response (201):
{
  "id": "payout-uuid",
  "status": "pending",
  "amount_paise": 100000,
  "created_at": "2026-04-30T10:00:00Z"
}
```

### Get Payout Status

```bash
GET /api/v1/payouts/{payout_id}/

Response:
{
  "id": "payout-uuid",
  "status": "completed",
  "attempt_count": 1,
  "last_attempted_at": "2026-04-30T10:00:03Z"
}
```

### Get Balance

```bash
GET /api/v1/merchants/{merchant_id}/balance/

Response:
{
  "ledger_balance": 500000,
  "held_balance": 0,
  "available_balance": 500000
}
```

### View Ledger

```bash
GET /api/v1/merchants/{merchant_id}/ledger/

Response:
[
  {
    "id": "entry-uuid",
    "entry_type": "debit",
    "amount_paise": 100000,
    "description": "Payout completed",
    "created_at": "2026-04-30T10:00:00Z"
  }
]
```

## 🧪 Testing

```bash
# Run tests
docker-compose exec backend python manage.py test

# Run specific test
docker-compose exec backend python manage.py test apps.payouts.tests
```

Tests verify:
- ✅ Concurrent payout creation (no race conditions)
- ✅ Idempotency (duplicate requests)
- ✅ Balance calculation accuracy
- ✅ Ledger entry atomicity
- ✅ State transitions

## 🔍 Monitoring

### Celery Tasks

```bash
# View Celery logs
docker-compose logs -f celery-worker

# Check beat schedule
docker-compose logs -f celery-beat
```

### Database

```bash
# Connect to database
docker-compose exec db psql -U postgres -d playto_payout

# Check stuck payouts
SELECT * FROM payouts_payout WHERE status='processing' AND attempt_count < 3;

# View recent ledger entries
SELECT * FROM merchants_ledgerentry ORDER BY created_at DESC LIMIT 10;
```

## 🛠️ Configuration

### Adjust Success Rate

Edit `backend/apps/payouts/tasks.py`:

```python
def simulate_bank_settlement():
    r = random.random()
    if r < 0.90:        # Success: 90% (vs 70% default)
        return 'success'
    elif r < 0.98:      # Failure: 8% (vs 20% default)
        return 'failure'
    else:               # Hang: 2% (vs 10% default)
        time.sleep(5)
        return 'hang'
```

Restart: `docker-compose restart celery-worker`

### Adjust Retry Schedule

Edit `backend/config/celery.py`:

```python
app.conf.beat_schedule = {
    'retry-stuck-payouts': {
        'task': 'apps.payouts.tasks.retry_stuck_payouts',
        'schedule': crontab(minute='*/1'),  # Check every 1 minute
    },
}
```

## 🚨 Troubleshooting

### Payout stuck in "processing"?

**Expected behavior** for 10% of payouts (simulated slow bank). Auto-retries after 60 seconds.

```bash
# Check retry logs
docker-compose logs -f celery-worker | grep retry
```

### Ledger entry not showing?

Check payout status:
```bash
curl http://localhost:8000/api/v1/payouts/{payout_id}/
```

Ledger entries appear only when payout reaches final status (`completed` or `failed`).

### Balance calculation wrong?

```bash
# Manual verification
docker-compose exec backend python manage.py shell

>>> from apps.merchants.services import get_merchant_balance
>>> get_merchant_balance(merchant_id)
```

## 📚 Documentation

- **README.md** — This file (quick start & API reference)
- **EXPLAINER.md** — Architecture decisions, design patterns, and payout flow diagrams

See **EXPLAINER.md** for:
- Deep dives on concurrency control, idempotency, and state machines
- Detailed payout flow diagrams for all three scenarios
- Balance calculation examples with step-by-step walkthroughs
- FAQ and troubleshooting commands

## 📝 Project Structure

```
playto-payout/
├── backend/                  # Django backend
│   ├── config/              # Settings, URLs, Celery
│   ├── apps/
│   │   ├── merchants/       # Merchant management
│   │   └── payouts/         # Payout processing
│   ├── tests/               # Test suite
│   ├── manage.py
│   ├── seed.py
│   └── requirements.txt
├── frontend/                 # JavaScript dashboard
│   ├── src/
│   ├── public/
│   ├── index.html
│   └── package.json
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── .env.example
└── README.md
```

## 📧 Support

For detailed information about:
- **Architecture decisions** — See EXPLAINER.md (Questions 1-5)
- **Concurrency patterns** — See EXPLAINER.md Question 2
- **Payout flows** — See EXPLAINER.md (Payout Flow Diagrams section)
- **Balance calculations** — See EXPLAINER.md Question 1
