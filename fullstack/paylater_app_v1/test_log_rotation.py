import requests
import time

url = "http://127.0.0.1:8000/token(login)"
email = "ani@gmail.com"
correct_password = "ani123"
wrong_password = "wrongpass"

total_attempts = 100
success_needed = 30
success_count = 0
failure_count = 0

for i in range(total_attempts):
    # First 30 attempts successful, remaining 70 failed
    if i < success_needed:
        data = {"email": email, "password": correct_password}
        print(f"[{i+1}] Successful login attempt...")
    else:
        data = {"email": email, "password": wrong_password}
        print(f"[{i+1}] Failed login attempt...")

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            success_count += 1
        else:
            failure_count += 1
        print(f"Response: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Request failed: {e}")
        failure_count += 1

    time.sleep(0.1)

print(f"\nSummary: {success_count} successful logins, {failure_count} failed logins.")
