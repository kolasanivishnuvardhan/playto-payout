#!/bin/bash
# Quick Deployment Script for Render + Vercel

echo "🚀 Playto Payout - Deployment Setup"
echo "===================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git not initialized"
    echo "Run: git init"
    exit 1
fi

echo "✅ Git repository found"

# Stage all changes
echo ""
echo "📝 Staging changes..."
git add .
git status

# Commit
echo ""
echo "💾 Committing changes..."
read -p "Enter commit message (default: 'Add deployment configuration'): " commit_msg
commit_msg=${commit_msg:-"Add deployment configuration"}
git commit -m "$commit_msg"

# Push
echo ""
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Changes pushed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://render.com"
echo "2. Sign in with GitHub"
echo "3. Click 'New +' → 'Blueprint'"
echo "4. Select this repository"
echo "5. Render will detect render.yaml automatically"
echo "6. Click 'Deploy'"
echo ""
echo "7. Once backend is deployed, go to https://vercel.com"
echo "8. Import the same repository"
echo "9. Set REACT_APP_API_URL environment variable"
echo ""
echo "🎉 Done! Both services will be deployed."
