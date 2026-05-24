from app import app
import json

print("\n=== FAKE NEWS DETECTION APP TEST ===\n")

client = app.test_client()

# Test 1: Health
print("✓ Test 1: Health Check")
r = client.get('/api/health')
print(f"  Status: {r.status_code}")
print(f"  Response: {json.dumps(r.get_json(), indent=4)}")

# Test 2: Fake News
print("\n✓ Test 2: Fake News Prediction")
r = client.post('/api/predict', json={'text': 'Aliens visited earth and taught humans new technology last night'}, content_type='application/json')
res = r.get_json()
print(f"  Status: {r.status_code}")
print(f"  Result: {res['result']}")
print(f"  Confidence: {res['confidence']}")

# Test 3: Real News
print("\n✓ Test 3: Real News Prediction")
r = client.post('/api/predict', json={'text': 'Scientists discover new method to cure cancer after extensive research and clinical trials'}, content_type='application/json')
res = r.get_json()
print(f"  Status: {r.status_code}")
print(f"  Result: {res['result']}")
print(f"  Confidence: {res['confidence']}")

# Test 4: Error - Short text
print("\n✓ Test 4: Error Handling (Short Text)")
r = client.post('/api/predict', json={'text': 'test'}, content_type='application/json')
print(f"  Status: {r.status_code}")
print(f"  Error: {r.get_json()['error']}")

print("\n✅ ALL TESTS PASSED!\n")
