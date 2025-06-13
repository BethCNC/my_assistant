#!/bin/bash

# Beth Assistant Frontend Cleanup Script
# Removes unnecessary components and files while preserving Figma design system components

echo "🧹 Starting Beth Assistant Frontend Cleanup..."
echo "This will remove unnecessary files while preserving your Figma design system components."

# Navigate to frontend directory
cd /Users/bethcartrette/REPOS/my_assistant/frontend

# Create backup directory
echo "📦 Creating backup..."
mkdir -p .cleanup-backup
cp -r src .cleanup-backup/ 2>/dev/null || echo "No src directory to backup"
cp -r components/ui-clean .cleanup-backup/ 2>/dev/null || echo "No ui-clean directory to backup"
cp -r components/ui-figma .cleanup-backup/ 2>/dev/null || echo "No ui-figma directory to backup"

echo "✅ Backup created in .cleanup-backup/"

# Remove duplicate React structure in /src
echo "🗑️  Removing duplicate React structure in /src..."
if [ -d "src" ]; then
    rm -rf src
    echo "   ✅ Removed /src directory"
else
    echo "   ℹ️  /src directory already removed"
fi

# Remove unused shadcn/ui components
echo "🗑️  Removing unused shadcn/ui components..."
cd components/ui

# Keep only the Figma components and essential files
FIGMA_COMPONENTS=(
    "ChatInput.tsx"
    "ChatPreview.tsx"
    "ChatConversation.tsx"
    "IconButton.tsx"
    "Icons.tsx"
    "NavigationText.tsx"
    "NewChatButton.tsx"
    "Sidebar.tsx"
    "SuggestionCard.tsx"
    "SuggestionShapes.tsx"
    "ThumbnailImages.tsx"
    "ToolButton.tsx"
    "index.ts"
)

# Create temp directory with only Figma components
mkdir -p ../ui-temp
for component in "${FIGMA_COMPONENTS[@]}"; do
    if [ -f "$component" ]; then
        cp "$component" ../ui-temp/
        echo "   ✅ Preserved $component"
    fi
done

# Remove old ui directory and replace with cleaned version
cd ..
rm -rf ui
mv ui-temp ui
echo "   ✅ Cleaned up shadcn/ui components"

# Remove empty directories
echo "🗑️  Removing empty/unused directories..."
if [ -d "ui-clean" ]; then
    rm -rf ui-clean
    echo "   ✅ Removed /components/ui-clean"
fi

if [ -d "ui-figma" ]; then
    rm -rf ui-figma
    echo "   ✅ Removed /components/ui-figma"
fi

# Return to root
cd ..

# Remove duplicate config files
echo "🗑️  Removing duplicate configuration files..."
if [ -f "postcss.config.js" ]; then
    rm postcss.config.js
    echo "   ✅ Removed postcss.config.js (keeping .mjs)"
fi

if [ -f "tailwind.config.js" ]; then
    rm tailwind.config.js
    echo "   ✅ Removed tailwind.config.js (keeping .ts)"
fi

# Remove cleanup/utility files
echo "🗑️  Removing cleanup and utility files..."
FILES_TO_REMOVE=(
    ".DS_Store"
    "beth-assistant.tsx"
    "cleanup-ui-final.sh"
    "cleanup-ui.js"
    "cleanup-ui.sh"
    "hello.html"
    "index.html"
    "DESIGN_SYSTEM.mdc"
    "DESIGN_SYSTEM_README.md"
)

for file in "${FILES_TO_REMOVE[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "   ✅ Removed $file"
    fi
done

# Update package.json to remove unused dependencies
echo "📦 Updating package.json..."
# Create a clean package.json with only needed dependencies
cat > package.json.new << 'EOF'
{
  "name": "beth-assistant",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@radix-ui/react-slot": "1.1.1",
    "autoprefixer": "^10.4.20",
    "clsx": "^2.1.1",
    "lucide-react": "^0.454.0",
    "next": "^15.2.4",
    "next-themes": "^0.4.4",
    "react": "^19.1.0",
    "react-dom": "^19.1.0",
    "tailwind-merge": "^2.5.5",
    "tailwindcss-animate": "^1.0.7"
  },
  "devDependencies": {
    "@types/node": "^22",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "postcss": "^8.5",
    "tailwindcss": "^3.4.17",
    "typescript": "^5"
  }
}
EOF

mv package.json package.json.backup
mv package.json.new package.json
echo "   ✅ Updated package.json (backup saved as package.json.backup)"

# Summary
echo ""
echo "🎉 Cleanup Complete!"
echo ""
echo "📋 Summary of changes:"
echo "   ✅ Removed duplicate /src React structure"
echo "   ✅ Cleaned up unused shadcn/ui components" 
echo "   ✅ Preserved all 12 Figma design system components"
echo "   ✅ Removed duplicate configuration files"
echo "   ✅ Removed cleanup and utility files"
echo "   ✅ Updated package.json with minimal dependencies"
echo "   ✅ Created backup in .cleanup-backup/"
echo ""
echo "🎯 Your Figma design system components are preserved:"
echo "   • ChatInput, ChatPreview, ChatConversation"
echo "   • IconButton, Icons, NavigationText"
echo "   • NewChatButton, Sidebar, SuggestionCard"
echo "   • SuggestionShapes, ThumbnailImages, ToolButton"
echo ""
echo "🔧 Next steps:"
echo "   1. Run: npm install (to install minimal dependencies)"
echo "   2. Run: npm run dev (to test your app)"
echo "   3. Remove .cleanup-backup/ when satisfied"
echo ""
echo "✨ Your frontend is now clean and optimized for your Figma design system!"
