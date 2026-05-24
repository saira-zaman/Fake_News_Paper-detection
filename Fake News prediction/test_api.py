"""
Comprehensive test script for Fake News Detection API
Tests all endpoints and functionality before Vercel deployment
"""

import requests
import json
import sys

# Configuration
API_URL = "http://localhost:5000"
TIMEOUT = 10

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(message, status="INFO"):
    """Print status messages with colors"""
    if status == "OK":
        print(f"{Colors.GREEN}[OK]{Colors.END} {message}")
    elif status == "ERROR":
        print(f"{Colors.RED}[ERROR]{Colors.END} {message}")
    elif status == "WARNING":
        print(f"{Colors.YELLOW}[WARNING]{Colors.END} {message}")
    else:
        print(f"{Colors.BLUE}[INFO]{Colors.END} {message}")

def test_health_check():
    """Test health check endpoint"""
    print_status("Testing Health Check Endpoint...", "INFO")
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_status(f"Health Check: {data}", "OK")
            return True
        else:
            print_status(f"Health check failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Health check error: {e}", "ERROR")
        return False

def test_home_page():
    """Test home page"""
    print_status("Testing Home Page...", "INFO")
    try:
        response = requests.get(f"{API_URL}/", timeout=TIMEOUT)
        if response.status_code == 200:
            print_status("Home page loaded successfully", "OK")
            return True
        else:
            print_status(f"Home page failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Home page error: {e}", "ERROR")
        return False

def test_prediction(text, expected_type=None):
    """Test prediction endpoint"""
    print_status(f"Testing Prediction with text: '{text[:50]}...'", "INFO")
    try:
        payload = {"text": text}
        response = requests.post(
            f"{API_URL}/api/predict",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_status(f"Prediction: {data['result']}", "OK")
                print_status(f"Confidence: {data['confidence']}", "OK")
                return True
            else:
                print_status(f"Prediction failed: {data.get('error')}", "ERROR")
                return False
        else:
            print_status(f"Prediction HTTP error: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Prediction error: {e}", "ERROR")
        return False

def test_error_cases():
    """Test error handling"""
    print_status("Testing Error Handling...", "INFO")
    
    test_cases = [
        ("", "Empty text"),
        ("Hi", "Too short text"),
        (None, "None payload"),
    ]
    
    all_passed = True
    for text, description in test_cases:
        try:
            payload = {"text": text} if text is not None else {}
            response = requests.post(
                f"{API_URL}/api/predict",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=TIMEOUT
            )
            
            if response.status_code in [400, 400]:
                print_status(f"Error case '{description}' handled correctly", "OK")
            else:
                print_status(f"Error case '{description}' not handled: {response.status_code}", "WARNING")
                all_passed = False
        except Exception as e:
            print_status(f"Error case test failed: {e}", "ERROR")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}=== Fake News Detection API Tests ==={Colors.END}\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("Home Page", test_home_page),
        ("Real News Prediction", lambda: test_prediction(
            "The government announced new climate policies today. Officials stated that carbon emissions will be reduced by 50% by 2030. This decision comes after years of research and international negotiations."
        )),
        ("Fake News Prediction", lambda: test_prediction(
            "SHOCKING: Aliens spotted near area 51! Secret government conspiracy revealed! Scientists claim UFOs are visiting Earth weekly!"
        )),
        ("Error Handling", test_error_cases),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            print(f"\n{Colors.BLUE}>> {test_name}{Colors.END}")
            results[test_name] = test_func()
        except Exception as e:
            print_status(f"Test '{test_name}' crashed: {e}", "ERROR")
            results[test_name] = False
    
    # Summary
    print(f"\n{Colors.BLUE}=== Test Summary ==={Colors.END}\n")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}[{status}]{Colors.END} {test_name}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} tests passed{Colors.END}\n")
    
    if passed == total:
        print_status("All tests passed! Ready for Vercel deployment.", "OK")
        return 0
    else:
        print_status(f"{total - passed} test(s) failed.", "ERROR")
        return 1

if __name__ == "__main__":
    if not sys.argv[1:]:
        print("Starting tests...")
        sys.exit(main())
    else:
        print("Usage: python test_api.py")
