#!/usr/bin/env python3
"""
Test script to verify Groq API configuration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Groq Configuration Test ===\n")

# Check environment variables
print("1. Checking environment variables:")
print(f"   DELL_LLM_ENDPOINT: {os.getenv('DELL_LLM_ENDPOINT')}")
print(f"   DELL_LLM_API_KEY: {os.getenv('DELL_LLM_API_KEY')[:20]}... (truncated)")
print(f"   DELL_LLM_MODEL: {os.getenv('DELL_LLM_MODEL')}")

# Test Groq connection
print("\n2. Testing Groq connection:")
try:
    from openai import OpenAI
    
    client = OpenAI(
        base_url=os.getenv('DELL_LLM_ENDPOINT'),
        api_key=os.getenv('DELL_LLM_API_KEY')
    )
    print("   ✓ OpenAI client initialized")
    
    # Test chat completion
    print("\n3. Testing chat completion:")
    try:
        response = client.chat.completions.create(
            model=os.getenv('DELL_LLM_MODEL'),
            messages=[
                {"role": "user", "content": "Hello, can you hear me? Please respond with just 'Yes, I can hear you'."}
            ],
            max_tokens=50
        )
        print("   ✓ Chat completion successful")
        if hasattr(response, 'choices') and len(response.choices) > 0:
            print(f"   Response: {response.choices[0].message.content}")
        else:
            print(f"   Response: {str(response)}")
    except Exception as e:
        print(f"   ✗ Chat completion failed: {e}")
    
except ImportError as e:
    print(f"   ✗ Failed to import openai: {e}")
    print("   Install with: pip install openai")
except Exception as e:
    print(f"   ✗ Groq connection failed: {e}")

print("\n=== Test Complete ===")
