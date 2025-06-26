#!/usr/bin/env python3
"""
Test script for Figma variables extraction.
Run this after updating your Figma token with the correct scopes.
"""

import os
import json
from figma import figma_service

def test_figma_variables():
    """Test Figma variables extraction and documentation generation."""
    
    # Your Figma file key
    file_key = "8dak7GzHKjjMohUxhu9M9A"
    
    print("🎨 Testing Figma Variables Extraction")
    print("=" * 50)
    print(f"File Key: {file_key}")
    print(f"Figma Token: {'SET' if os.getenv('FIGMA_ACCESS_TOKEN') else 'NOT SET'}")
    print()
    
    try:
        # Test 1: Extract variables
        print("📊 Step 1: Extracting variables...")
        variables_result = figma_service.get_file_variables(file_key)
        
        if not variables_result['success']:
            print(f"❌ Error: {variables_result.get('error')}")
            if 'details' in variables_result:
                print(f"Details: {variables_result['details']}")
            return False
        
        print(f"✅ Success! Found {variables_result['total_collections']} collections")
        print(f"   Total variables: {variables_result['total_variables']}")
        
        # Show collections summary
        for collection_id, collection in variables_result['collections'].items():
            print(f"   📁 {collection['name']}: {len(collection['variables'])} variables")
        
        print()
        
        # Test 2: Generate documentation
        print("📝 Step 2: Generating documentation...")
        doc_result = figma_service.generate_variables_documentation(file_key, 'markdown')
        
        if not doc_result['success']:
            print(f"❌ Documentation error: {doc_result.get('error')}")
            return False
        
        print(f"✅ Documentation generated successfully!")
        
        # Save documentation to file
        doc_filename = f"figma_variables_documentation_{file_key}.md"
        with open(doc_filename, 'w', encoding='utf-8') as f:
            f.write(doc_result['markdown'])
        
        print(f"   📄 Saved to: {doc_filename}")
        
        # Show documentation summary
        doc_data = doc_result['documentation']
        print(f"   📊 Primitives: {len(doc_data['primitives'])} collections")
        print(f"   🔗 Alias: {len(doc_data['alias'])} collections") 
        print(f"   🎯 Semantics: {len(doc_data['semantics'])} collections")
        print(f"   📦 Other: {len(doc_data['other'])} collections")
        
        print()
        
        # Test 3: Show sample variables
        print("🔍 Step 3: Sample variables preview...")
        sample_count = 0
        for collection_id, collection in variables_result['collections'].items():
            if sample_count >= 2:  # Show max 2 collections
                break
                
            print(f"   📁 Collection: {collection['name']}")
            
            for i, variable in enumerate(collection['variables'][:3]):  # Show max 3 variables
                var_name = variable['name']
                var_type = variable.get('type', 'Unknown')
                print(f"      • {var_name} ({var_type})")
                
                # Show values for first mode
                if variable.get('values'):
                    first_mode = list(variable['values'].keys())[0]
                    value = variable['values'][first_mode]
                    if isinstance(value, dict) and 'r' in value:
                        # Color value
                        r = int(value['r'] * 255)
                        g = int(value['g'] * 255) 
                        b = int(value['b'] * 255)
                        print(f"        Value: rgb({r}, {g}, {b})")
                    else:
                        print(f"        Value: {str(value)[:50]}")
            
            if len(collection['variables']) > 3:
                print(f"      ... and {len(collection['variables']) - 3} more variables")
            
            print()
            sample_count += 1
        
        print("🎉 All tests passed! Your Figma variables are ready for documentation.")
        return True
        
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_figma_variables()
    exit(0 if success else 1) 