# 🚀 Quick Start: Deploy to Production

## Step 1: Authenticate Services
```bash
# Re-authenticate Firebase
firebase login --reauth

# Authenticate Google Cloud
gcloud auth login
gcloud config set project beth-personal-assistant
```

## Step 2: Setup Production Environment
```bash
# Run the automated setup script
npm run setup:production
```

This will create:
- `frontend/.env.production` - Frontend environment variables
- `beth_health_journey_app/.env.production` - Health app environment variables
- `firestore.rules` - Database security rules
- `frontend/public/manifest.json` - PWA manifest

## Step 3: Configure Environment Variables

### Frontend Environment Variables
Edit `frontend/.env.production`:
```env
# Get these from Firebase Console > Project Settings > General
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyC...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=beth-personal-assistant.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=beth-personal-assistant

# Update after backend deployment (Step 4)
NEXT_PUBLIC_API_URL=https://beth-assistant-backend-XXXXXXX-uc.a.run.app
```

### Health Journey Environment Variables
Edit `beth_health_journey_app/.env.production`:
```env
# Supabase credentials (if using)
NEXT_PUBLIC_SUPABASE_URL=https://gflraidtzkqhkwxraama.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...

# Your API keys
NOTION_TOKEN=secret_...
OPENAI_API_KEY=sk-...
FIGMA_API_TOKEN=figd_...
```

## Step 4: Deploy Backend First
```bash
# Deploy Python backend to Google Cloud Run
npm run deploy:backend
```

**Important**: Copy the deployed backend URL and update `NEXT_PUBLIC_API_URL` in `frontend/.env.production`

## Step 5: Deploy Frontend
```bash
# Deploy frontend to Firebase Hosting
npm run deploy:web
```

## Step 6: Deploy Everything (Alternative)
```bash
# Deploy both backend and frontend
npm run deploy:all
```

## Step 7: Set Up Custom Domain (Optional)

### In Firebase Console:
1. Go to Hosting section
2. Click "Add custom domain"
3. Enter your domain name
4. Follow DNS setup instructions

### Quick DNS Setup:
```
Type: A
Name: @
Value: 151.101.1.195

Type: A  
Name: @
Value: 151.101.65.195
```

## Verify Deployment

### Check Backend Health
```bash
curl https://your-backend-url.run.app/health
```

### Check Frontend
Visit: `https://beth-personal-assistant.web.app`

### Check Desktop App
```bash
npm run build:desktop
# Find app in dist/ folder
```

## Troubleshooting

### Build Errors
```bash
# Clean everything and rebuild
npm run clean
npm run build
```

### Authentication Issues
```bash
# Re-authenticate
firebase login --reauth
gcloud auth login
```

### Environment Variable Issues
```bash
# Check variables are loaded
cd frontend && npm run build
cd beth_health_journey_app && npm run build
```

## Production URLs

After deployment, your apps will be available at:

- **Web App**: `https://beth-personal-assistant.web.app`
- **Custom Domain**: `https://yourdomain.com` (after Step 7)
- **Backend API**: `https://beth-assistant-backend-XXXXXXX-uc.a.run.app`
- **Desktop App**: Available in `dist/` folder after `npm run build:desktop`

## Next Steps

1. ✅ Test all app functionality in production
2. ✅ Set up monitoring and error tracking
3. ✅ Configure backup strategies
4. ✅ Set up CI/CD pipeline (optional)
5. ✅ Configure SSL and security headers

## Daily Deployment Workflow

```bash
# Make changes to your code
# Then deploy with:
npm run deploy:all
```

## Emergency Rollback

```bash
# List previous releases
firebase hosting:sites:releases:list

# Rollback to previous version
firebase hosting:sites:releases:restore RELEASE_ID
``` 