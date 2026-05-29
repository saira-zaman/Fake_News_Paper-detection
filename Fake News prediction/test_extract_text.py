from app import app
from io import BytesIO
import json

print("\n=== EXTRACT TEXT ENDPOINT TEST ===\n")

client = app.test_client()

# Test TXT upload
print("✓ Test: TXT file upload")
data = {
    'file': (BytesIO(b'This is a sample news article.\nLine two of article.'), 'sample.txt')
}
resp = client.post('/api/extract-text', data=data, content_type='multipart/form-data')
print(f"  Status: {resp.status_code}")
print(f"  Response: {json.dumps(resp.get_json(), indent=2)}")

if resp.status_code == 200 and resp.get_json().get('success'):
    print('\n✅ Extract-text test passed')
else:
    print('\n❌ Extract-text test failed')
