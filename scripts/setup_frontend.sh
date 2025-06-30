#!/bin/bash

echo "🎨 Setting up Beth's Assistant Frontend..."

# Navigate to frontend directory
cd frontend

# Create environment file if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "🔧 Creating frontend environment file..."
    cat > .env.local << EOF
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    echo "✅ Created .env.local"
fi

# Install dependencies
echo "📦 Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup complete!"
echo "📝 Next steps:"
echo "   1. Run: cd frontend && npm run dev"
echo "   2. Open http://localhost:3000 in your browser" 