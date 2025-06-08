# 🚀 Beth's Assistant - Deployment Guide

## **Option 1: Railway (Recommended) - Full Stack**

### **Why Railway?**
✅ Python/FastAPI native support  
✅ SQLite persistent storage  
✅ Custom domain included  
✅ Environment variables built-in  
✅ Auto-deploys from GitHub  

### **Setup Steps:**

1. **Install Railway CLI**
```bash
curl -fsSL https://railway.app/install.sh | sh
```

2. **Login and Initialize**
```bash
railway login
railway init
```

3. **Set Environment Variables**
```bash
railway env set OPENAI_API_KEY="your-openai-key"
railway env set NOTION_TOKEN="your-notion-token"
railway env set FIGMA_ACCESS_TOKEN="your-figma-token"
railway env set GITHUB_TOKEN="your-github-token"
railway env set GMAIL_CLIENT_ID="your-gmail-client-id"
railway env set GMAIL_CLIENT_SECRET="your-gmail-client-secret"
railway env set CALENDAR_CLIENT_ID="your-calendar-client-id"
railway env set CALENDAR_CLIENT_SECRET="your-calendar-client-secret"
```

4. **Deploy**
```bash
railway up
```

5. **Custom Domain**
- Go to Railway dashboard
- Settings → Domains
- Add: `assistant.yourdomain.com`
- Update DNS: `CNAME assistant -> your-railway-url`

---

## **Option 2: Vercel + Railway Split**

### **Frontend (Vercel)**

1. **Deploy Frontend**
```bash
cd test-vite
npm run build
vercel --prod
```

2. **Custom Domain**
- Vercel dashboard → Domains
- Add: `assistant.yourdomain.com`

### **Backend (Railway)**

1. **Deploy Backend Only**
```bash
cd backend
railway init
railway up
```

2. **Update Frontend API URL**
```javascript
// In your React app, update API calls:
const API_BASE = 'https://your-backend.railway.app'
```

---

## **Option 3: Render**

1. **Connect GitHub Repo**
2. **Create Web Service**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
3. **Add Environment Variables**
4. **Custom Domain**: Add in Render settings

---

## **Environment Variables Needed**

```env
OPENAI_API_KEY=sk-...
NOTION_TOKEN=secret_...
FIGMA_ACCESS_TOKEN=figd_...
GITHUB_TOKEN=ghp_...
GMAIL_CLIENT_ID=...apps.googleusercontent.com
GMAIL_CLIENT_SECRET=...
CALENDAR_CLIENT_ID=...apps.googleusercontent.com  
CALENDAR_CLIENT_SECRET=...
```

---

## **Database Considerations**

### **SQLite (Current)**
✅ Simple setup  
✅ No external dependencies  
✅ Perfect for personal use  
⚠️ Single-user limitations  

### **PostgreSQL (Upgrade Option)**
If you want multi-user support later:
```bash
railway add postgresql
# Update database connection in backend/main.py
```

---

## **Production Checklist**

- [ ] Environment variables set
- [ ] Custom domain configured  
- [ ] HTTPS enabled (automatic on Railway/Vercel)
- [ ] Database backup strategy
- [ ] Error monitoring (Railway has built-in)
- [ ] CORS configured for production domain

---

## **Quick Start Commands**

**Railway (Recommended):**
```bash
railway login
railway init --name "beth-assistant"
railway env set OPENAI_API_KEY="your-key"
# ... other env vars
railway up
```

**Test locally first:**
```bash
cd backend && uvicorn main:app --reload --port 8000
cd test-vite && npm run dev
``` 