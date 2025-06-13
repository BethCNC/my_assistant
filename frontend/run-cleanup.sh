#!/bin/bash

echo "🔧 Running directory cleanup..."

cd /Users/bethcartrette/REPOS/my_assistant/frontend

# Remove the old confusing directories
echo "Removing old directories..."
rm -rf components/ui 2>/dev/null || echo "ui directory already removed"
rm -rf components/ui-clean 2>/dev/null || echo "ui-clean directory already removed"  
rm -rf components/ui-figma 2>/dev/null || echo "ui-figma directory already removed"

echo "✅ Cleanup complete!"
echo ""
echo "📋 Current structure:"
ls -la components/

echo ""
echo "🎯 figma-system components:"
ls -1 components/figma-system/ | grep -E "\.tsx$|\.ts$"
