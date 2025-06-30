# Figma Variables Extraction Setup Guide

## 🎯 Goal
Extract and document all variable collections (primitives, alias, semantics) from your [Figma design system file](https://www.figma.com/design/8dak7GzHKjjMohUxhu9M9A/beth-assistant-design-system-file?node-id=4033-47756&t=jQFxZOA7KCKTObVi-1).

## 🔑 Required Figma API Token Scopes

Your current Figma token is missing the required scope. You need to create a new token with these scopes:

### ✅ Required Scopes:
- `file_variables:read` - **CRITICAL** for accessing variables
- `file_content:read` - For reading file structure  
- `file_metadata:read` - For file information
- `library_content:read` - For design system libraries

### 🔧 How to Get the Right Token:

1. **Go to Figma Settings**: https://www.figma.com/settings
2. **Navigate to**: Account Settings → Personal Access Tokens
3. **Create New Token** with these scopes:
   ```
   ✅ file_variables:read
   ✅ file_content:read  
   ✅ file_metadata:read
   ✅ library_content:read
   ```
4. **Copy the token** and update your environment variable

## 🚀 API Endpoints Ready

Once you have the correct token, these endpoints are ready to use:

### 1. Get All Variables
```bash
GET /api/figma/variables/8dak7GzHKjjMohUxhu9M9A
```

### 2. Generate Documentation  
```bash
GET /api/figma/variables/8dak7GzHKjjMohUxhu9M9A/documentation?format=markdown
```

### 3. Analyze Variables with RAG
```bash
POST /api/figma/variables/analyze
{
  "file_key": "8dak7GzHKjjMohUxhu9M9A",
  "focus_areas": ["primitives", "alias", "semantics"],
  "generate_recommendations": true
}
```

## 📋 What You'll Get

### Variable Collections Documentation:
- **Primitives Collections**: Base design tokens (colors, typography, spacing)
- **Alias Collections**: Semantic references to primitives  
- **Semantics Collections**: Context-specific tokens (themes, components)

### Detailed Information:
- Variable names, types, descriptions
- Values across different modes (light/dark themes)
- Alias relationships and dependencies
- Usage scopes and publishing status

### RAG-Enhanced Analysis:
- Design system optimization recommendations
- Consistency analysis across collections
- Usage pattern insights

## 🔧 Quick Test Commands

Once your token is updated:

```bash
# Test variables extraction
curl -s http://localhost:8000/api/figma/variables/8dak7GzHKjjMohUxhu9M9A | jq .

# Generate documentation
curl -s "http://localhost:8000/api/figma/variables/8dak7GzHKjjMohUxhu9M9A/documentation?format=markdown" | jq -r '.markdown' > figma_variables_docs.md

# Analyze with RAG
curl -s -X POST http://localhost:8000/api/figma/variables/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "file_key": "8dak7GzHKjjMohUxhu9M9A",
    "focus_areas": ["primitives", "alias", "semantics"],
    "generate_recommendations": true
  }' | jq .
```

## 🎨 Expected Output Structure

```json
{
  "success": true,
  "collections": {
    "collection_id": {
      "name": "Primitives/Colors",
      "modes": [
        {"name": "Light", "modeId": "1:0"},
        {"name": "Dark", "modeId": "1:1"}
      ],
      "variables": [
        {
          "name": "color/primary/500",
          "type": "COLOR",
          "values": {
            "1:0": {"r": 0.2, "g": 0.4, "b": 0.8, "a": 1},
            "1:1": {"r": 0.3, "g": 0.5, "b": 0.9, "a": 1}
          }
        }
      ]
    }
  }
}
```

## 🔄 Next Steps

1. **Update your Figma token** with the correct scopes
2. **Restart the backend server** 
3. **Run the test commands** to extract your variables
4. **Review the generated documentation** for your design system

The system is ready to systematically pull and document all your Figma variables as soon as the token permissions are updated! 