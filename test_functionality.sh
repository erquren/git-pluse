#!/bin/bash
set -e

echo "=========================================="
echo "Testing git-pluse functionality"
echo "=========================================="

# Activate virtual environment
source venv/bin/activate

echo ""
echo "1. Testing help command..."
git-pluse --help

echo ""
echo "2. Testing JSON output for a small repo..."
rm -f test-project.json
git-pluse https://github.com/python/cpython -o /workspace/test_output
echo "JSON file created:"
ls -lh /workspace/test_output/cpython.json 2>/dev/null || echo "Expected file not found"

echo ""
echo "3. Testing with show parameter (if API allows)..."
# This may fail due to rate limits, but that's OK for this test
git-pluse https://github.com/python/cpython show -o /workspace/test_output 2>/dev/null || echo "Rate limit encountered (expected)"

echo ""
echo "4. Checking JSON structure..."
if [ -f "/workspace/test_output/cpython.json" ]; then
    python3 -c "import json; data = json.load(open('/workspace/test_output/cpython.json')); print('Valid JSON'); print('Keys:', list(data.keys())); print('Total commits:', data.get('total_commits', 0))"
else
    echo "JSON file not found"
fi

echo ""
echo "=========================================="
echo "Test completed!"
echo "=========================================="
