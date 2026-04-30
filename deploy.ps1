# Quick Deployment Script for Render + Vercel (PowerShell)

Write-Host "🚀 Playto Payout - Deployment Setup" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "❌ Git not initialized" -ForegroundColor Red
    Write-Host "Run: git init" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Git repository found" -ForegroundColor Green
Write-Host ""

# Stage all changes
Write-Host "📝 Staging changes..." -ForegroundColor Cyan
git add .
git status

# Commit
Write-Host ""
Write-Host "💾 Committing changes..." -ForegroundColor Cyan
$commit_msg = Read-Host "Enter commit message (default: 'Add deployment configuration')"
if ([string]::IsNullOrWhiteSpace($commit_msg)) {
    $commit_msg = "Add deployment configuration"
}
git commit -m $commit_msg

# Push
Write-Host ""
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Cyan
git push origin main

Write-Host ""
Write-Host "✅ Changes pushed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "STEP 1: Deploy Backend to Render" -ForegroundColor Cyan
Write-Host "  1. Go to https://render.com" -ForegroundColor White
Write-Host "  2. Sign in with GitHub" -ForegroundColor White
Write-Host "  3. Click 'New +' → 'Blueprint'" -ForegroundColor White
Write-Host "  4. Select playto-payout repository" -ForegroundColor White
Write-Host "  5. Render auto-detects render.yaml" -ForegroundColor White
Write-Host "  6. Click 'Deploy'" -ForegroundColor White
Write-Host "  7. Wait 5-10 minutes for deployment" -ForegroundColor White
Write-Host ""
Write-Host "STEP 2: Seed Test Data on Render" -ForegroundColor Cyan
Write-Host "  1. Go to Render dashboard" -ForegroundColor White
Write-Host "  2. Click Web Service → Shell" -ForegroundColor White
Write-Host "  3. Run command:" -ForegroundColor White
Write-Host "     python backend/manage.py seed_dynamic_data --merchants 10 --transactions 20" -ForegroundColor Magenta
Write-Host ""
Write-Host "STEP 3: Deploy Frontend to Vercel" -ForegroundColor Cyan
Write-Host "  1. Go to https://vercel.com" -ForegroundColor White
Write-Host "  2. Sign in with GitHub" -ForegroundColor White
Write-Host "  3. Click 'Add New' → 'Project'" -ForegroundColor White
Write-Host "  4. Select playto-payout repository" -ForegroundColor White
Write-Host "  5. Set Root Directory: frontend" -ForegroundColor White
Write-Host "  6. Add Environment Variable:" -ForegroundColor White
Write-Host "     REACT_APP_API_URL=https://<your-render-api-url>/api/v1" -ForegroundColor Magenta
Write-Host "  7. Click 'Deploy'" -ForegroundColor White
Write-Host ""
Write-Host "STEP 4: Update CORS in Backend" -ForegroundColor Cyan
Write-Host "  1. Edit backend/config/settings.py" -ForegroundColor White
Write-Host "  2. Add your Vercel URL to CORS_ALLOWED_ORIGINS" -ForegroundColor White
Write-Host "  3. Git commit and push" -ForegroundColor White
Write-Host "  4. Render will auto-redeploy" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Done! Your system is deployed!" -ForegroundColor Green
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Yellow
Write-Host "  Frontend: https://playto-payout-frontend-xxx.vercel.app" -ForegroundColor Cyan
Write-Host "  Backend:  https://playto-payout-api-xxx.onrender.com" -ForegroundColor Cyan
Write-Host "  Admin:    https://playto-payout-api-xxx.onrender.com/admin" -ForegroundColor Cyan
