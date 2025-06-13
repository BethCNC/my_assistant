#!/bin/bash

# Beth Assistant - Clean Directory Structure
# This script removes the confusing ui, ui-clean, ui-figma directories
# and keeps only the clean figma-system directory

echo "🧹 Cleaning up confusing component directory structure..."
echo "This will remove ui, ui-clean, ui-figma and keep only figma-system"

# Navigate to frontend directory
cd /Users/bethcartrette/REPOS/my_assistant/frontend

# Create backup
echo "📦 Creating backup..."
mkdir -p .directory-cleanup-backup
cp -r components .directory-cleanup-backup/
echo "   ✅ Full components backup created"

# Remove confusing directories
echo "🗑️  Removing confusing directories..."

if [ -d "components/ui" ]; then
    rm -rf components/ui
    echo "   ✅ Removed components/ui"
fi

if [ -d "components/ui-clean" ]; then
    rm -rf components/ui-clean
    echo "   ✅ Removed components/ui-clean"
fi

if [ -d "components/ui-figma" ]; then
    rm -rf components/ui-figma
    echo "   ✅ Removed components/ui-figma"
fi

# Verify figma-system directory exists and is complete
echo "✅ Verifying figma-system directory..."
if [ -d "components/figma-system" ]; then
    echo "   ✅ figma-system directory exists"
    
    # Count components
    COMPONENT_COUNT=$(find components/figma-system -name "*.tsx" | wc -l)
    echo "   ✅ Found $COMPONENT_COUNT components in figma-system"
    
    # List components
    echo "   📋 Components in figma-system:"
    ls -1 components/figma-system/*.tsx | sed 's/.*\///; s/\.tsx//' | sed 's/^/      • /'
else
    echo "   ❌ ERROR: figma-system directory missing!"
    echo "   🔄 Restoring from backup..."
    cp -r .directory-cleanup-backup/components .
    exit 1
fi

# Summary
echo ""
echo "🎉 Directory cleanup complete!"
echo ""
echo "📋 New clean structure:"
echo "   components/"
echo "   ├── BethAssistantSystematic.tsx"
echo "   ├── ChatInterface.tsx"
echo "   ├── ChatInterface.module.css"
echo "   ├── theme-provider.tsx"
echo "   └── figma-system/            ← All your Figma components"
echo "       ├── ChatInput.tsx"
echo "       ├── ChatPreview.tsx"
echo "       ├── ChatConversation.tsx"
echo "       ├── IconButton.tsx"
echo "       ├── Icons.tsx"
echo "       ├── NavigationText.tsx"
echo "       ├── NewChatButton.tsx"
echo "       ├── Sidebar.tsx"
echo "       ├── SuggestionCard.tsx"
echo "       ├── SuggestionShapes.tsx"
echo "       ├── ThumbnailImages.tsx"
echo "       ├── ToolButton.tsx"
echo "       └── index.ts"
echo ""
echo "✅ Benefits:"
echo "   • No more confusion about which components to use"
echo "   • Clear separation: figma-system contains ONLY Figma components"
echo "   • All components are pixel-perfect implementations"
echo "   • Easy imports: @/components/figma-system/ComponentName"
echo ""
echo "🔧 Next steps:"
echo "   1. Test your app: npm run dev"
echo "   2. All imports have been updated to use figma-system"
echo "   3. Remove backup when satisfied: rm -rf .directory-cleanup-backup"
echo ""
echo "✨ Your component structure is now clean and organized!"
