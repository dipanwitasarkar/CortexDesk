#!/usr/bin/env python3
"""
Simple test for local gpt2 without full dependencies
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import asyncio

print("=== Simple gpt2 Test ===\n")

print("1. Loading gpt2 model...")
try:
    tokenizer = AutoTokenizer.from_pretrained('gpt2', local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained('gpt2', local_files_only=True)
    model.eval()
    print("   ✓ Model loaded successfully")
    print(f"   Model size: {sum(p.numel() for p in model.parameters())} parameters")
    
    print("\n2. Testing generation...")
    test_prompt = "Hello, can you help me with my coding task?"
    inputs = tokenizer(test_prompt, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
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
    
    print("\n3. Testing multiple generations...")
    test_prompts = [
        "What is Python?",
        "How do I write a function?",
        "Explain machine learning."
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=30, do_sample=True, temperature=0.7, pad_token_id=tokenizer.eos_token_id)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"   Test {i}: {prompt}")
        print(f"   Response: {response.replace(prompt, '').strip()}")
        print()
    
    print("=== Test Complete ===")
    print("\nNote: gpt2 is a small 2019 model with limited capabilities.")
    print("Responses may be nonsensical or irrelevant - this is normal.")
    
except Exception as e:
    print(f"   ✗ Test failed: {e}")
    print("\n=== Test Failed ===")
