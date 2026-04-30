# Deployment Guide: Vercel + Backend Options

## ⚠️ Important: Vercel Limitations

Vercel is **optimized for frontend apps**, not full-stack Django + PostgreSQL + Redis + Celery.

### What Vercel CAN do:
✅ Frontend (JavaScript dashboard) at vercel.com

### What Vercel CANNOT do:
❌ Django backend (needs persistent Python runtime)
❌ PostgreSQL database (needs persistent storage)
❌ Redis (needs persistent in-memory store)
❌ Celery workers (needs persistent background tasks)

---

## 🎯 Recommended Deployment Architecture

### Option 1: Vercel Frontend + Heroku Backend (EASIEST)

```
Your Architecture:
├── Frontend: Vercel (free tier)
├── Backend: Heroku (paid tier, ~$7-50/month)
├── Database: Heroku PostgreSQL
├── Queue: Heroku Redis
└── Workers: Heroku Dyno
```

**Pros:**
- ✅ Simple deployment
- ✅ Free frontend tier
- ✅ Managed databases
- ✅ Easy to manage

**Cons:**
- ❌ Backend costs money
- ❌ Limited free resources

**Time to Deploy:** 30 minutes

---

### Option 2: Vercel Frontend + Railway Backend (RECOMMENDED)

```
Your Architecture:
├── Frontend: Vercel (free tier)
├── Backend: Railway (pay-as-you-go, ~$5-15/month)
├── Database: Railway PostgreSQL
├── Queue: Railway Redis
└── Workers: Railway Container
```

**Pros:**
- ✅ Modern platform
- ✅ Better than Heroku
- ✅ Free trial credits
- ✅ Docker-friendly

**Cons:**
- ❌ Backend costs money
- ❌ Smaller community

**Time to Deploy:** 30 minutes

---

### Option 3: Vercel Frontend + AWS Backend (SCALABLE)

```
Your Architecture:
├── Frontend: Vercel (free tier)
├── Backend: AWS EC2 (free tier first year, then ~$5-20/month)
├── Database: AWS RDS PostgreSQL
├── Queue: AWS ElastiCache Redis
└── Workers: EC2 Instance
```

**Pros:**
- ✅ Highly scalable
- ✅ Free tier available
- ✅ Industry standard

**Cons:**
- ❌ Complex setup
- ❌ More expensive long-term

**Time to Deploy:** 2-3 hours

---

### Option 4: Docker on Render (EASIEST FULL-STACK)

```
Your Architecture:
├── Frontend: Vercel (free tier)
└── Backend: Render (free tier available)
    ├── Django API
    ├── PostgreSQL
    ├── Redis
    └── Worker service
```

**Pros:**
- ✅ Simplest for full Docker stack
- ✅ Free tier available
- ✅ One-click deploy

**Cons:**
- ❌ Free tier limited resources
- ❌ May need paid plan

**Time to Deploy:** 20 minutes

---

## 📋 Quick Comparison

| Platform | Frontend | Backend | Database | Cost | Setup Time |
|----------|----------|---------|----------|------|-----------|
| **Vercel + Heroku** | ✅ | ✅ | ✅ | $7-50/mo | 30 min |
| **Vercel + Railway** | ✅ | ✅ | ✅ | $5-15/mo | 30 min |
| **Vercel + AWS** | ✅ | ✅ | ✅ | $5-20/mo | 2-3 hrs |
| **Vercel + Render** | ✅ | ✅ | ✅ | Free-$7/mo | 20 min |
| **Docker (Render)** | ✅ | ✅ | ✅ | Free-$7/mo | 20 min |

---

## 🚀 RECOMMENDED: Deploy Both on Render (Full Stack)

### Why Render?
- Single platform for everything
- Docker support (use your docker-compose.yml)
- Free tier available
- Easiest migration from Docker

### Architecture
```
Render:
├── Web Service (Django Backend)
├── Worker Service (Celery)
├── PostgreSQL Database
└── Redis Cache

Vercel:
└── Static Frontend
```

---

## 📋 Step-by-Step: Render Full-Stack Deployment

### Part 1: Prepare Your Code for Render

#### Step 1.1: Create render.yaml (at root level)

Create file: `d:\playto-payout\render.yaml`

```yaml
services:
  - type: web
    name: playto-payout-api
    runtime: python
    plan: free
    pythonVersion: 3.11
    
    envVars:
      - key: DJANGO_SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: ALLOWED_HOSTS
        value: "*.render.com,*.vercel.app"
      - key: DJANGO_SUPERUSER_PASSWORD
        scope: secret
      - key: DATABASE_URL
        fromDatabase:
          name: playto-payout-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: playto-payout-redis
          property: connectionString
    
    buildCommand: |
      pip install -r backend/requirements.txt && \
      python backend/manage.py collectstatic --noinput && \
      python backend/manage.py migrate
    
    startCommand: gunicorn backend.config.wsgi:application --bind 0.0.0.0:$PORT

  - type: worker
    name: playto-payout-worker
    runtime: python
    plan: free
    pythonVersion: 3.11
    
    envVars:
      - key: CELERY_BROKER_URL
        fromService:
          name: playto-payout-redis
          property: connectionString
      - key: CELERY_RESULT_BACKEND
        fromService:
          name: playto-payout-redis
          property: connectionString
      - key: DATABASE_URL
        fromDatabase:
          name: playto-payout-db
          property: connectionString
    
    buildCommand: pip install -r backend/requirements.txt
    startCommand: celery -A config worker --loglevel=info

  - type: pserv
    name: playto-payout-beat
    runtime: python
    plan: free
    pythonVersion: 3.11
    
    envVars:
      - key: CELERY_BROKER_URL
        fromService:
          name: playto-payout-redis
          property: connectionString
      - key: DATABASE_URL
        fromDatabase:
          name: playto-payout-db
          property: connectionString
    
    buildCommand: pip install -r backend/requirements.txt
    startCommand: celery -A config beat --loglevel=info

databases:
  - name: playto-payout-db
    engine: postgres
    plan: free
    version: 15
    ipAllowList:
      - key: render
        value: "0.0.0.0/0"

  - name: playto-payout-redis
    engine: redis
    plan: free
    version: 7
    ipAllowList:
      - key: render
        value: "0.0.0.0/0"
```

#### Step 1.2: Add Gunicorn to requirements.txt

Edit `backend/requirements.txt`:

```
Add line:
gunicorn==21.2.0
```

#### Step 1.3: Update Django Settings for Production

Edit `backend/config/settings.py`, add:

```python
import os

# Render deployment settings
if os.environ.get('RENDER'):
    DEBUG = False
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
    
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
```

### Part 2: Deploy to Render

#### Step 2.1: Push to GitHub

```bash
cd d:\playto-payout
git add render.yaml backend/requirements.txt backend/config/settings.py
git commit -m "Add Render deployment configuration"
git push origin main
```

#### Step 2.2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize GitHub access

#### Step 2.3: Deploy from GitHub

1. On Render dashboard, click **"New +"** → **"Blueprint"**
2. Select your GitHub repository
3. Render will auto-detect `render.yaml`
4. Click **"Deploy"**
5. Wait 5-10 minutes for build and deployment

#### Step 2.4: Set Environment Variables

1. Go to Web Service settings
2. Add under **"Environment"**:
   ```
   DJANGO_SECRET_KEY: <generate-random-key>
   DJANGO_SUPERUSER_PASSWORD: <your-secure-password>
   ```
3. Redeploy

#### Step 2.5: Run Migrations

1. On Render, go to **"Shell"** tab
2. Run:
   ```bash
   python backend/manage.py migrate
   python backend/manage.py createsuperuser
   ```

### Part 3: Seed Test Data

#### Step 3.1: SSH into Render

```bash
# Via Render Shell tab
python backend/manage.py seed_dynamic_data --merchants 10 --transactions 20
```

Or from your local terminal:

```bash
# Deploy custom management command
python backend/manage.py seed_dynamic_data
```

#### Step 3.2: Verify Data

```bash
# Via Render Shell
python backend/manage.py shell

>>> from apps.merchants.models import Merchant
>>> print(Merchant.objects.count())
10  # Should show seeded merchants
```

---

## 🎨 Step-by-Step: Deploy Frontend to Vercel

### Part 1: Prepare Frontend

#### Step 1.1: Create vercel.json

Create file: `d:\playto-payout\frontend\vercel.json`

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "env": {
    "REACT_APP_API_URL": "@playto-payout-api-url"
  }
}
```

#### Step 1.2: Update Frontend to Use Backend URL

Edit `frontend/src/App.js`:

```javascript
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
```

#### Step 1.3: Push to GitHub

```bash
git add frontend/vercel.json frontend/src/App.js
git commit -m "Update frontend for Vercel deployment"
git push origin main
```

### Part 2: Deploy to Vercel

#### Step 2.1: Create Vercel Account

1. Go to https://vercel.com
2. Sign up with GitHub
3. Authorize GitHub access

#### Step 2.2: Import Project

1. On Vercel dashboard, click **"Add New"** → **"Project"**
2. Select your GitHub repository
3. Click **"Import"**

#### Step 2.3: Configure Project

1. **Project Name:** playto-payout-frontend
2. **Root Directory:** `frontend`
3. **Build Command:** `npm run build`
4. **Output Directory:** `build`
5. **Environment Variables:**
   ```
   REACT_APP_API_URL: https://your-render-api-url.onrender.com/api/v1
   ```

#### Step 2.4: Deploy

1. Click **"Deploy"**
2. Wait 2-5 minutes
3. Get your Vercel URL: `https://playto-payout-frontend-xxx.vercel.app`

---

## 🎯 Final Setup: Connect Frontend to Backend

### Step 1: Get Backend URL from Render

```
https://playto-payout-api-xxx.onrender.com
```

### Step 2: Update Vercel Environment Variables

1. On Vercel dashboard, go to **Settings** → **Environment Variables**
2. Add:
   ```
   REACT_APP_API_URL=https://playto-payout-api-xxx.onrender.com/api/v1
   ```
3. Redeploy

### Step 3: Update Backend CORS

Edit `backend/config/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://playto-payout-frontend-xxx.vercel.app',
]
```

### Step 4: Commit and Push

```bash
git add backend/config/settings.py
git commit -m "Update CORS for Vercel deployment"
git push origin main
```

---

## ✅ Deployment Checklist

- [ ] render.yaml created
- [ ] gunicorn added to requirements.txt
- [ ] settings.py updated for production
- [ ] All changes pushed to GitHub
- [ ] Render blueprint deployed
- [ ] Migrations run on Render
- [ ] Test data seeded
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set
- [ ] CORS configured
- [ ] Frontend can connect to backend

---

## 🧪 Testing Deployed System

### Test Backend API

```bash
curl https://playto-payout-api-xxx.onrender.com/api/v1/merchants/
```

Should return:
```json
[
  {
    "id": "uuid",
    "name": "Test Merchant 1",
    ...
  }
]
```

### Test Frontend

1. Open https://playto-payout-frontend-xxx.vercel.app
2. Should load dashboard
3. Try creating a payout
4. Should process in 2-3 seconds

### Test Celery Workers

```bash
# Via Render Shell
python backend/manage.py shell

>>> from apps.payouts.models import Payout
>>> p = Payout.objects.all().first()
>>> print(p.status)  # Should show: completed/failed
```

---

## 📊 Costs Breakdown

| Service | Tier | Cost |
|---------|------|------|
| Vercel | Hobby (Free) | $0 |
| Render Web | Free | $0 (first 750 hours/month) |
| Render Worker | Free | $0 (first 750 hours/month) |
| Render Beat | Free | $0 (first 750 hours/month) |
| Render PostgreSQL | Free | $0 (limited) |
| Render Redis | Free | $0 (limited) |
| **TOTAL** | | **$0-15/month** |

After free tier exhausted:
- Render web: $7/month
- Total: ~$7-15/month for production

---

## 🚨 Troubleshooting

### Build Fails on Render

```bash
# Check logs
# Go to Render dashboard → Select service → Logs tab
# Look for errors

# Common issues:
❌ Missing dependencies → Add to requirements.txt
❌ Python version mismatch → Update pythonVersion in render.yaml
❌ Database connection → Check DATABASE_URL env var
```

### Frontend Can't Connect to Backend

```bash
# Check CORS settings
# Check API URL in frontend env vars
# Check backend is running (curl the API)
```

### Data Not Seeded

```bash
# SSH into Render and run manually
python backend/manage.py seed_dynamic_data --merchants 50 --transactions 25

# Or create via API
curl -X POST https://playto-payout-api-xxx.onrender.com/api/v1/merchants/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Merchant"}'
```

### Workers Not Processing Payouts

```bash
# Check Render worker logs
# Verify CELERY_BROKER_URL is set
# Verify Redis is running
# Check scheduled tasks: celery -A config inspect active
```

---

## 📚 Next Steps

1. ✅ Prepare code for deployment
2. ✅ Deploy backend to Render
3. ✅ Deploy frontend to Vercel
4. ✅ Seed test data
5. → Monitor and optimize
6. → Set up custom domain (optional)
7. → Add CI/CD automation

---

**Ready to deploy? Start with Render!** 🚀
