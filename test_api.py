import requests
import json

BASE_URL = "http://127.0.0.1:5000/search"

def test_api(data, expected_status_code, expected_response=None):
    response = requests.post(BASE_URL, json=data)
    print(f"\nTest case: {data}")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    assert response.status_code == expected_status_code, f"Expected status code {expected_status_code}, but got {response.status_code}"
    
    if expected_response:
        response_json = response.json()
        assert response_json == expected_response, f"Expected response {expected_response}, but got {response_json}"
    
    print("Test passed successfully!")

# Test 1: Valid request
valid_data = {
    "keyword": "ccpackaging",
    "pages": 1
}
test_api(valid_data, 200)

# Test 2: Missing keyword
missing_keyword_data = {
    "pages": 1
}
test_api(missing_keyword_data, 400, {"error": "Keyword is required"})

# Test 3: Invalid pages value
invalid_pages_data = {
    "keyword": "example search term",
    "pages": "two"
}
test_api(invalid_pages_data, 400, {"error": "Number of pages must be an integer"})

print("\nAll tests completed.")