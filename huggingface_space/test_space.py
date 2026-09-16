#!/usr/bin/env python3
"""
Test script to verify Hugging Face Space is working
"""
import requests
import json

# Replace with your actual Space URL
SPACE_URL = "https://your-space-name.hf.space"

print("=== Hugging Face Space Test ===\n")

# Test health endpoint
print("1. Testing health endpoint:")
try:
    response = requests.get(f"{SPACE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test chat completions
print("\n2. Testing chat completions:")
try:
    payload = {
        "messages": [
            {"role": "user", "content": "Hello, can you hear me?"}
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    response = requests.post(
        f"{SPACE_URL}/v1/chat/completions",
        json=payload
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if "choices" in result:
            print(f"   Response: {result['choices'][0]['message']['content'][:100]}...")
        else:
            print(f"   Response: {result}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

print("\n=== Test Complete ===")
