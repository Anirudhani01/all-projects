#!/usr/bin/env python3
"""
Script to initialize the RBAC system with default roles and permissions
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb
from app.rbac.initializer import RBACInitializer

async def initialize_rbac():
    """Initialize the RBAC system"""
    try:
        print("🚀 Initializing RBAC system...")
        
        # Connect to database first
        await mongodb.connect()
        
        # Get database connection
        database = mongodb.get_database()
        
        # Initialize RBAC
        initializer = RBACInitializer(database)
        result = await initializer.initialize()
        
        print("✅ RBAC system initialized successfully!")
        
        # Print the roles that were created
        print("\n📋 Created roles:")
        for role_name, role_id in result.get('roles', {}).items():
            print(f"  - {role_name}: {role_id}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error initializing RBAC: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(initialize_rbac())
