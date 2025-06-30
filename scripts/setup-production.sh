#!/bin/bash

echo "🔧 Setting up production environment for Beth Assistant..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're authenticated with Firebase
echo -e "${BLUE}Checking Firebase authentication...${NC}"
if ! firebase projects:list > /dev/null 2>&1; then
    echo -e "${RED}❌ Firebase authentication required${NC}"
    echo -e "${YELLOW}Please run: firebase login --reauth${NC}"
    exit 1
fi

# Check if we're authenticated with Google Cloud
echo -e "${BLUE}Checking Google Cloud authentication...${NC}"
if ! gcloud auth list --filter="status:ACTIVE" --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Google Cloud authentication required${NC}"
    echo -e "${YELLOW}Please run: gcloud auth login${NC}"
    exit 1
fi

# Create frontend production environment file
if [ ! -f "frontend/.env.production" ]; then
    echo -e "${BLUE}Creating frontend/.env.production...${NC}"
    cat > frontend/.env.production << 'EOF'
# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=beth-personal-assistant.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=beth-personal-assistant

# Backend API (update after backend deployment)
NEXT_PUBLIC_API_URL=https://beth-assistant-backend-XXXXXXX-uc.a.run.app

# Optional: Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
EOF
    echo -e "${YELLOW}⚠️  Please update frontend/.env.production with your actual values${NC}"
else
    echo -e "${GREEN}✅ frontend/.env.production already exists${NC}"
fi

# Create health journey app production environment file
if [ ! -f "beth_health_journey_app/.env.production" ]; then
    echo -e "${BLUE}Creating beth_health_journey_app/.env.production...${NC}"
    cat > beth_health_journey_app/.env.production << 'EOF'
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

# Medical Database IDs (from Notion)
NOTION_MEDICAL_CALENDAR_ID=17b86edcae2c81c183e0e0a19a035932
NOTION_SYMPTOMS_DATABASE_ID=17b86edcae2c81c69077e55a68cf2438
NOTION_MEDICAL_TEAM_ID=17b86edcae2c81558caafbb80647f6a9
NOTION_MEDICATIONS_ID=17b86edcae2c81a7b28ae9fbcc7e7b62
NOTION_NOTES_ID=654e1ddc962f44698b1df6697375a321
EOF
    echo -e "${YELLOW}⚠️  Please update beth_health_journey_app/.env.production with your actual values${NC}"
else
    echo -e "${GREEN}✅ beth_health_journey_app/.env.production already exists${NC}"
fi

# Create PWA manifest if it doesn't exist
if [ ! -f "frontend/public/manifest.json" ]; then
    echo -e "${BLUE}Creating PWA manifest...${NC}"
    cat > frontend/public/manifest.json << 'EOF'
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
    },
    {
      "src": "/assets/smiley.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
EOF
    echo -e "${GREEN}✅ PWA manifest created${NC}"
fi

# Update frontend next.config.mjs for production export
if [ -f "frontend/next.config.mjs" ]; then
    echo -e "${BLUE}Updating frontend Next.js config for production export...${NC}"
    cat > frontend/next.config.mjs << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    NEXT_PUBLIC_FIREBASE_API_KEY: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    NEXT_PUBLIC_FIREBASE_PROJECT_ID: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  experimental: {
    optimizeCss: true,
  }
}

export default nextConfig
EOF
    echo -e "${GREEN}✅ Frontend config updated for production export${NC}"
fi

# Update health journey app next config
if [ -f "beth_health_journey_app/next.config.js" ]; then
    echo -e "${BLUE}Updating health journey Next.js config...${NC}"
    cat > beth_health_journey_app/next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  },
  experimental: {
    optimizeCss: true,
  }
}

module.exports = nextConfig
EOF
    echo -e "${GREEN}✅ Health journey config updated${NC}"
fi

# Create Firebase security rules if they don't exist
if [ ! -f "firestore.rules" ]; then
    echo -e "${BLUE}Creating Firestore security rules...${NC}"
    cat > firestore.rules << 'EOF'
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Only authenticated users can access data
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
EOF
    echo -e "${GREEN}✅ Firestore security rules created${NC}"
fi

# Create firestore indexes if they don't exist
if [ ! -f "firestore.indexes.json" ]; then
    echo -e "${BLUE}Creating Firestore indexes...${NC}"
    cat > firestore.indexes.json << 'EOF'
{
  "indexes": [],
  "fieldOverrides": []
}
EOF
    echo -e "${GREEN}✅ Firestore indexes file created${NC}"
fi

# Make the script executable
chmod +x setup-production.sh

echo ""
echo -e "${GREEN}✅ Production environment setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Update environment variables in ${BLUE}frontend/.env.production${NC}"
echo -e "2. Update environment variables in ${BLUE}beth_health_journey_app/.env.production${NC}"
echo -e "3. Deploy backend: ${BLUE}npm run deploy:backend${NC}"
echo -e "4. Deploy frontend: ${BLUE}npm run deploy:web${NC}"
echo -e "5. Or deploy everything: ${BLUE}npm run deploy:all${NC}"
echo ""
echo -e "${BLUE}For custom domain setup, see PRODUCTION_DEPLOYMENT.md${NC}" 