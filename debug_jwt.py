import requests
import json

# Test the login endpoint
login_url = "http://localhost:5000/api/v1/auth/login"
login_data = {
    "username": "recorder001",
    "password": "recorder123"
}

print("Testing login...")
response = requests.post(login_url, json=login_data)
print(f"Login status code: {response.status_code}")
print(f"Login response: {response.text}")

if response.status_code == 200:
    login_result = response.json()
    access_token = login_result['data']['access_token']
    refresh_token = login_result['data']['refresh_token']
    
    print(f"\nAccess token: {access_token}")
    print(f"Refresh token: {refresh_token}")
    
    # Test the refresh endpoint
    print("\nTesting refresh token...")
    refresh_url = "http://localhost:5000/api/v1/auth/refresh"
    refresh_headers = {
        "Authorization": f"Bearer {refresh_token}"
    }
    refresh_response = requests.post(refresh_url, headers=refresh_headers)
    print(f"Refresh status code: {refresh_response.status_code}")
    print(f"Refresh response: {refresh_response.text}")
    
    # Test a protected endpoint
    print("\nTesting protected endpoint...")
    families_url = "http://localhost:5000/api/v1/families"
    families_headers = {
        "Authorization": f"Bearer {access_token}"
    }
    families_response = requests.get(families_url, headers=families_headers)
    print(f"Families status code: {families_response.status_code}")
    print(f"Families response: {families_response.text}")
else:
    print("Login failed!")