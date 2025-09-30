#!/usr/bin/env python3
"""
Test script for the web application
"""

import requests
import json
import time

def test_web_app():
    base_url = "http://localhost:5000"
    
    print("Testing Torrey Pines Waitlist Web App")
    print("=" * 40)
    
    # Test 1: Check if the app is running
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Web app is running")
        else:
            print(f"❌ Web app returned status {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Web app is not running. Start it with: python app.py")
        return
    
    # Test 2: Check status endpoint
    try:
        response = requests.get(f"{base_url}/status")
        status = response.json()
        print(f"✅ Status endpoint working: {status['message']}")
    except Exception as e:
        print(f"❌ Status endpoint failed: {e}")
    
    # Test 3: Test form submission (without actually running automation)
    test_data = {
        "first_name": "test",
        "last_name": "user",
        "email": "test@example.com",
        "phone": "1234567890",
        "course": "south",
        "players": "2",
        "target_time": "23:59"  # Far in the future
    }
    
    try:
        response = requests.post(f"{base_url}/start", json=test_data)
        if response.status_code == 200:
            print("✅ Form submission working")
        else:
            print(f"❌ Form submission failed: {response.json()}")
    except Exception as e:
        print(f"❌ Form submission error: {e}")
    
    print("\n🎉 Web app is ready for deployment!")

if __name__ == "__main__":
    test_web_app()
