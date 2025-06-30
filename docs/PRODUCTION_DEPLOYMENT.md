# 🚀 Production Deployment Guide

## Pre-Deployment Checklist

### 1. Authentication Setup
```bash
# Re-authenticate Firebase
firebase login --reauth

# Verify Google Cloud access
gcloud auth login
gcloud config set project beth-personal-assistant
```

### 2. Environment Variables Setup

#### Frontend Environment Variables
Create `frontend/.env.production`:
```env
# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=beth-personal-assistant.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=beth-personal-assistant

# Backend API
NEXT_PUBLIC_API_URL=https://beth-assistant-backend-your-url.run.app

# Supabase (if using)
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

#### Health Journey App Environment Variables
Create `beth_health_journey_app/.env.production`:
```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Notion Integration
NOTION_TOKEN=your-notion-integration-token
NOTION_API_KEY=your-notion-integration-token

# OpenAI for Medical Data Processing
OPENAI_API_KEY=your-openai-api-key

# Figma Design Tokens
FIGMA_API_TOKEN=your-figma-token
FIGMA_FILE_KEY=your-figma-file-id
```

#### Backend Environment Variables
Update `backend/cloudbuild.yaml` with real secrets:
```yaml
- "--set-env-vars"
- "NOTION_TOKEN=actual_notion_token,FIGMA_ACCESS_TOKEN=actual_figma_token,GITHUB_TOKEN=actual_github_token,OPENAI_API_KEY=actual_openai_key"
```

## 🌐 Domain Configuration

### Step 1: Configure Custom Domain in Firebase
```bash
# Add your custom domain
firebase hosting:sites:create your-domain-name
firebase target:apply hosting main your-domain-name

# Update firebase.json for custom domain
```

### Step 2: Update Firebase Configuration
Update `firebase.json`:
```json
{
  "hosting": [
    {
      "target": "main",
      "public": "frontend/out",
      "ignore": [
        "firebase.json",
        "**/.*",
        "**/node_modules/**"
      ],
      "rewrites": [
        {
          "source": "/health/**",
          "destination": "/health/index.html"
        },
        {
          "source": "**",
          "destination": "/index.html"
        }
      ],
      "cleanUrls": true,
      "trailingSlash": false
    }
  ],
  "firestore": {
    "database": "(default)",
    "location": "nam5",
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  }
}
```

## 🏗️ Build & Deploy Process

### Step 1: Environment Setup Script
```bash
#!/bin/bash
# setup-production.sh

echo "🔧 Setting up production environment..."

# Create production environment files
if [ ! -f "frontend/.env.production" ]; then
    echo "Creating frontend/.env.production..."
    cp frontend/.env.production.example frontend/.env.production
    echo "⚠️  Please update frontend/.env.production with your actual values"
fi

if [ ! -f "beth_health_journey_app/.env.production" ]; then
    echo "Creating beth_health_journey_app/.env.production..."
    cp beth_health_journey_app/.env.production.example beth_health_journey_app/.env.production
    echo "⚠️  Please update beth_health_journey_app/.env.production with your actual values"
fi

echo "✅ Production environment setup complete!"
```

### Step 2: Updated Package.json Scripts
```json
{
  "scripts": {
    "dev": "cd frontend && npm run dev",
    "dev:health": "cd beth_health_journey_app && npm run dev",
    "dev:desktop": "concurrently \"npm run dev\" \"wait-on http://localhost:3000 && electron .\"",
    
    "build": "npm run build:frontend && npm run build:health",
    "build:frontend": "cd frontend && npm run build && npm run export",
    "build:health": "cd beth_health_journey_app && npm run build && npm run export",
    "build:desktop": "npm run build:frontend && npm run package:mac",
    
    "predeploy": "npm run setup:production && npm run build",
    "deploy:backend": "cd backend && gcloud builds submit --config cloudbuild.yaml",
    "deploy:web": "firebase deploy --only hosting:main",
    "deploy:all": "npm run predeploy && npm run deploy:backend && npm run deploy:web",
    
    "setup:production": "./setup-production.sh",
    "package:mac": "electron-packager . BethAssistant --platform=darwin --arch=arm64 --icon=frontend/public/assets/smiley.png --overwrite --out=dist",
    "clean": "rm -rf dist && rm -rf frontend/.next && rm -rf frontend/out && rm -rf beth_health_journey_app/.next && rm -rf beth_health_journey_app/out"
  }
}
```

### Step 3: Multi-App Hosting Strategy

#### Option A: Subdomain Approach
- Main app: `https://yourdomain.com`
- Health app: `https://health.yourdomain.com`

#### Option B: Path-Based Approach
- Main app: `https://yourdomain.com`
- Health app: `https://yourdomain.com/health`

## 🔒 Security Configuration

### 1. Firebase Security Rules
Create `firestore.rules`:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Only authenticated users can access data
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### 2. CORS Configuration
Update backend to handle CORS for your domain:
```python
# In backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://health.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Environment Secrets Management
Use Google Secret Manager for sensitive data:
```bash
# Store secrets in Google Secret Manager
gcloud secrets create notion-token --data-file=-
gcloud secrets create openai-api-key --data-file=-
gcloud secrets create supabase-service-key --data-file=-
```

## 📱 Progressive Web App (PWA) Setup

### 1. Add PWA Manifest
Create `frontend/public/manifest.json`:
```json
{
  "name": "Beth Assistant",
  "short_name": "BethAssistant",
  "description": "Personal health and assistant application",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#000000",
  "icons": [
    {
      "src": "/assets/smiley.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```

### 2. Service Worker for Offline Functionality
Update `frontend/next.config.mjs`:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  experimental: {
    // Enable PWA features
    optimizeCss: true,
  }
}

export default nextConfig
```

## 🚀 Deployment Commands

### Quick Deploy (After Initial Setup)
```bash
# Deploy everything to production
npm run deploy:all
```

### Individual Deployments
```bash
# Deploy only backend
npm run deploy:backend

# Deploy only frontend
npm run deploy:web

# Build desktop app
npm run build:desktop
```

### Emergency Rollback
```bash
# Rollback to previous version
firebase hosting:sites:releases:list
firebase hosting:sites:releases:restore RELEASE_ID
```

## 🔍 Monitoring & Health Checks

### 1. Health Check Endpoints
Add to backend:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

### 2. Frontend Monitoring
Add to `frontend/pages/_app.tsx`:
```typescript
// Error boundary and monitoring
useEffect(() => {
  if (process.env.NODE_ENV === 'production') {
    // Initialize error monitoring
    console.log('Production monitoring initialized');
  }
}, []);
```

## 📋 Post-Deployment Checklist

- [ ] SSL certificate active and valid
- [ ] Custom domain pointing correctly
- [ ] All environment variables configured
- [ ] Database connections working
- [ ] API endpoints responding
- [ ] Desktop app packaging successful
- [ ] PWA installable on mobile devices
- [ ] Error monitoring active
- [ ] Backup strategy implemented

## 🛠️ Troubleshooting

### Common Issues

1. **Build Failures**
   - Check environment variables are set
   - Verify all dependencies installed
   - Check for TypeScript errors

2. **Deploy Failures**
   - Verify Firebase authentication
   - Check Google Cloud permissions
   - Validate environment variables

3. **Runtime Errors**
   - Check browser console for errors
   - Verify API endpoints are accessible
   - Check CORS configuration

### Debug Commands
```bash
# Check Firebase status
firebase projects:list

# Test backend health
curl https://your-backend-url.run.app/health

# Check build output
npm run build && ls -la frontend/out

# Test desktop app locally
npm run dev:desktop
``` 