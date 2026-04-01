#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to start the enhanced_app server and test the /api/activities/recent API
"""

import sys
import os
import requests
import json

def test_api():
    """Test the activities API"""
    
    # First, get JWT token
    login_url = "http://127.0.0.1:5000/api/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # Login to get token
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"✅ Login successful. Token: {token[:20]}...")
            
            # Test activities API
            activities_url = "http://127.0.0.1:5000/api/activities/recent"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            activities_response = requests.get(activities_url, headers=headers)
            if activities_response.status_code == 200:
                activities = activities_response.json()
                print(f"✅ Activities API successful. Found {len(activities)} activities")
                print(json.dumps(activities, indent=2, ensure_ascii=False))
            else:
                print(f"❌ Activities API failed: {activities_response.status_code}")
                print(f"Response: {activities_response.text}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing /api/activities/recent API...")
    test_api()