#!/usr/bin/env python3
"""
Test script to verify Hugging Face Inference API configuration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Hugging Face Configuration Test ===\n")

# Check environment variables
print("1. Checking environment variables:")
print(f"   DELL_LLM_ENDPOINT: {os.getenv('DELL_LLM_ENDPOINT')}")
print(f"   DELL_LLM_API_KEY: {os.getenv('DELL_LLM_API_KEY')[:20]}... (truncated)")
print(f"   DELL_LLM_MODEL: {os.getenv('DELL_LLM_MODEL')}")
print(f"   DELL_LLM_EMBEDDING_MODEL: {os.getenv('DELL_LLM_EMBEDDING_MODEL')}")

# Test Hugging Face connection
print("\n2. Testing Hugging Face connection:")
try:
    from huggingface_hub import InferenceClient
    
    client = InferenceClient(token=os.getenv('DELL_LLM_API_KEY'))
    print("   ✓ Hugging Face client initialized")
    
    # Test conversational API
    print("\n3. Testing conversational API:")
    try:
        response = client.chat.completions.create(
            model=os.getenv('DELL_LLM_MODEL'),
            messages=[{"role": "user", "content": "Hello, can you hear me?"}],
            max_tokens=50
        )
        print(f"   ✓ Conversational API successful")
        if hasattr(response, 'choices') and len(response.choices) > 0:
            print(f"   Response: {response.choices[0].message.content[:100]}...")
        else:
            print(f"   Response: {str(response)[:100]}...")
    except Exception as e:
        print(f"   ✗ Conversational API failed: {e}")
        # Fallback to text generation
        print("\n   Trying text generation fallback:")
        try:
            response = client.text_generation(
                model=os.getenv('DELL_LLM_MODEL'),
                prompt="Hello, can you hear me?",
                max_new_tokens=50
            )
            print(f"   ✓ Text generation successful")
            print(f"   Response: {response[:100]}...")
        except Exception as e2:
            print(f"   ✗ Text generation also failed: {e2}")
    
    # Test feature extraction (embeddings)
    print("\n4. Testing feature extraction:")
    try:
        embedding = client.feature_extraction(
            model=os.getenv('DELL_LLM_EMBEDDING_MODEL'),
            text="Test text for embedding"
        )
        print(f"   ✓ Feature extraction successful")
        print(f"   Embedding dimension: {len(embedding) if isinstance(embedding, list) else 'N/A'}")
    except Exception as e:
        print(f"   ✗ Feature extraction failed: {e}")
    
except ImportError as e:
    print(f"   ✗ Failed to import huggingface_hub: {e}")
    print("   Install with: pip install huggingface-hub")
except Exception as e:
    print(f"   ✗ Hugging Face connection failed: {e}")

print("\n=== Test Complete ===")
