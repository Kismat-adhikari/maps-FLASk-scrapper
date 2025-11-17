"""
Quick test script for Apify Actor
Simulates Apify environment locally
"""

import asyncio
import json
import os
from main import main

# Set up test environment
os.environ['APIFY_IS_AT_HOME'] = '1'
os.environ['APIFY_DEFAULT_DATASET_ID'] = 'test-dataset'
os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID'] = 'test-kvs'

# Load test input
with open('test_input.json', 'r') as f:
    test_input = json.load(f)

# Save as Apify input
os.makedirs('.apify', exist_ok=True)
with open('.apify/INPUT.json', 'w') as f:
    json.dump(test_input, f, indent=2)

print("=" * 60)
print("TESTING APIFY ACTOR LOCALLY")
print("=" * 60)
print(f"\nInput: {json.dumps(test_input, indent=2)}")
print("\nStarting actor...\n")

# Run the actor
asyncio.run(main())

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
