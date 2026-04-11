#!/usr/bin/env python3
"""
Demo script for the Category Management System
This script demonstrates how to use the new category and subcategory features.
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def demo_category_management():
    """Demonstrate category management functionality."""
    
    print("🚀 Category Management System Demo")
    print("=" * 50)
    
    # Test 1: Create a category
    print("\n1️⃣ Creating a new category: 'Saree'")
    saree_category = {
        "name": "Saree",
        "slug": "saree",
        "description": "Traditional Indian sarees for all occasions",
        "image": "https://example.com/saree-category.jpg",
        "icon": "saree-icon",
        "isActive": True,
        "isFeatured": True,
        "sortOrder": 1
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/categories/", json=saree_category)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Category created successfully!")
            print(f"Category ID: {data['data']['id']}")
            print(f"Category Name: {data['data']['name']}")
            print(f"Category Slug: {data['data']['slug']}")
        else:
            print(f"❌ Failed to create category: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the FastAPI server is running.")
        print("   Run: python start_dev.py")
        return
    
    # Test 2: Create another category
    print("\n2️⃣ Creating another category: 'Kurta'")
    kurta_category = {
        "name": "Kurta",
        "slug": "kurta",
        "description": "Traditional Indian kurtas for men and women",
        "image": "https://example.com/kurta-category.jpg",
        "icon": "kurta-icon",
        "isActive": True,
        "isFeatured": False,
        "sortOrder": 2
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/categories/", json=kurta_category)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Kurta category created successfully!")
            print(f"Category ID: {data['data']['id']}")
        else:
            print(f"❌ Failed to create kurta category: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")
    
    # Test 3: Get all categories
    print("\n3️⃣ Getting all categories")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/categories/")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Categories retrieved successfully!")
            print(f"Total categories: {len(data['data'])}")
            for category in data['data']:
                print(f"  - {category['name']} ({category['slug']}) - {category['description']}")
        else:
            print(f"❌ Failed to get categories: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")
    
    # Test 4: Create a subcategory
    print("\n4️⃣ Creating a subcategory: 'Cotton Saree' under 'Saree'")
    
    # First, get the Saree category ID
    try:
        response = requests.get(f"{BASE_URL}/api/v1/categories/slug/saree")
        if response.status_code == 200:
            saree_data = response.json()
            saree_id = saree_data['data']['id']
            
            cotton_saree_subcategory = {
                "name": "Cotton Saree",
                "slug": "cotton-saree",
                "description": "Pure cotton sarees for daily wear"
            }
            
            response = requests.post(f"{BASE_URL}/api/v1/categories/{saree_id}/subcategories", 
                                  json=cotton_saree_subcategory)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Subcategory created successfully!")
                print(f"Subcategory Name: {data['data']['name']}")
                print(f"Subcategory Slug: {data['data']['slug']}")
            else:
                print(f"❌ Failed to create subcategory: {response.text}")
                
        else:
            print("❌ Could not find Saree category")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")
    
    # Test 5: Get category with subcategories
    print("\n5️⃣ Getting Saree category with subcategories")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/categories/slug/saree/with-subcategories")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Category with subcategories retrieved successfully!")
            print(f"Category: {data['data']['name']}")
            print(f"Subcategories: {len(data['data']['subcategories'])}")
            for subcat in data['data']['subcategories']:
                print(f"  - {subcat['name']} ({subcat['slug']})")
        else:
            print(f"❌ Failed to get category with subcategories: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")

def show_api_endpoints():
    """Show available API endpoints."""
    
    print("\n📚 Available Category API Endpoints")
    print("=" * 50)
    
    print("""
🔹 Category Management:
  POST   /api/v1/categories/                    # Create category (Admin)
  GET    /api/v1/categories/                    # Get all categories
  GET    /api/v1/categories/{id}                # Get category by ID
  GET    /api/v1/categories/slug/{slug}         # Get category by slug
  PUT    /api/v1/categories/{id}                # Update category (Admin)
  DELETE /api/v1/categories/{id}                # Delete category (Admin)

🔹 Subcategory Management:
  POST   /api/v1/categories/{id}/subcategories  # Create subcategory (Admin)
  GET    /api/v1/categories/{id}/subcategories  # Get subcategories
  GET    /api/v1/categories/{id}/with-subcategories # Get category + subcategories

🔹 Product Integration:
  - Products now support category and subcategory fields
  - Category product counts are automatically updated
  - Filtering by category and subcategory is supported
""")

def main():
    """Main function to run the demo."""
    
    print("🎯 E-commerce Category Management System")
    print("=" * 60)
    
    # Show API endpoints
    show_api_endpoints()
    
    # Run the demo
    demo_category_management()
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("\n💡 Key Features Implemented:")
    print("✅ Dynamic category creation and management")
    print("✅ Subcategory support for better organization")
    print("✅ Automatic product counting per category")
    print("✅ Slug-based routing for SEO-friendly URLs")
    print("✅ Admin-only creation/editing/deletion")
    print("✅ Product integration with categories")
    print("✅ Future-proof architecture")

if __name__ == "__main__":
    main()
