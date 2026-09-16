#!/usr/bin/env python3
"""
Test script to verify local gpt2 configuration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Local gpt2 Configuration Test ===\n")

# Check environment variables
print("1. Checking environment variables:")
print(f"   DELL_LLM_ENDPOINT: {os.getenv('DELL_LLM_ENDPOINT')}")
print(f"   DELL_LLM_MODEL: {os.getenv('DELL_LLM_MODEL')}")

# Test local model loading
print("\n2. Testing local model loading:")
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    
    model_name = os.getenv('DELL_LLM_MODEL', 'gpt2')
    print(f"   Loading {model_name}...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True)
    model.eval()
    
    print(f"   ✓ Model loaded successfully")
    print(f"   Model size: {sum(p.numel() for p in model.parameters())} parameters")
    print(f"   Device: {next(model.parameters()).device}")
    
    # Test generation
    print("\n3. Testing text generation:")
    test_prompt = "Hello, can you help me?"
    inputs = tokenizer(test_prompt, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=30,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"   ✓ Generation successful")
    print(f"   Prompt: {test_prompt}")
    print(f"   Response: {response.replace(test_prompt, '').strip()}")
    
except ImportError as e:
    print(f"   ✗ Failed to import transformers: {e}")
    print("   Install with: pip install transformers torch")
except Exception as e:
    print(f"   ✗ Local model test failed: {e}")

print("\n=== Test Complete ===")
