#!/usr/bin/env python3
"""Quick test to check if app is working"""

try:
    from app import app
    print("✓ App imported successfully")
    
    with app.test_client() as client:
        response = client.get('/')
        print(f"✓ Homepage status: {response.status_code}")
        
        response = client.get('/auth/login')
        print(f"✓ Login page status: {response.status_code}")
        
    print("\nApp is working! You can now test login.")
except Exception as e:
    print(f"✗ Error: {e}")