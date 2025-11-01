#!/usr/bin/env python3
"""
Quick test to verify regex cleaning works
"""

import re

# Test names with N/a
test_names = [
    "MARK RAINIER SORIANO COPIOSO N/a",
    "LENAR ANDREI PRIMNE YOLOLA N/a", 
    "JOHN DOE None",
    "JANE SMITH",
    "MARK RAINIER SORIANO COPIOSO  N/a",  # multiple spaces
]

print("🧪 Testing Regex Cleaning")
print("=" * 40)

for name in test_names:
    cleaned = re.sub(r'\s+N/a$', '', name, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+None$', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    
    print(f"Original: '{name}'")
    print(f"Cleaned:  '{cleaned}'")
    print()

print("✅ Testing complete")