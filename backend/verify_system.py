import requests
import time
import sys

BASE_URL = "http://localhost:8005/api/v1"

def run_test():
    print("1. Authenticating...")
    try:
        # Login to get token
        login_data = {
            "username": "admin@example.com",
            "password": "admin123"
        }
        r = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if r.status_code != 200:
            print(f"   Login Failed: {r.text}")
            return
            
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"   Login Successful. Token: {token[:10]}...")
    except Exception as e:
        print(f"   Failed: {e}")
        return

    print("\n2. Checking Health...")
    try:
        r = requests.get("http://localhost:8005/health")
        print(f"   Status: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"   Failed: {e}")

    print("\n3. Depositing Funds...")
    try:
        r = requests.post(f"{BASE_URL}/wallet/deposit", json={"amount": 50000}, headers=headers)
        if r.status_code != 200:
            print(f"   Failed: {r.status_code} - {r.text}")
        else:
            print(f"   Response: {r.json()}")
    except Exception as e:
        print(f"   Failed: {e}")

    print("\n4. Starting Trading Engine...")
    try:
        r = requests.post(f"{BASE_URL}/market/start", json={"symbol": "^NSEI"}, headers=headers)
        if r.status_code != 200:
            print(f"   Failed: {r.status_code} - {r.text}")
        else:
            print(f"   Response: {r.json()}")
    except Exception as e:
        print(f"   Failed: {e}")

    print("\n5. Checking Status...")
    try:
        r = requests.get(f"{BASE_URL}/market/status", headers=headers)
        print(f"   Response: {r.json()}")
    except Exception as e:
        print(f"   Failed: {e}")

    print("\n6. Waiting for 10 seconds (simulating trading)...")
    time.sleep(10)

    print("\n7. Checking Orders...")
    try:
        r = requests.get(f"{BASE_URL}/orders/", headers=headers)
        orders = r.json()
        print(f"   Orders found: {len(orders)}")
        if orders:
            print(f"   Latest Order: {orders[0]}")
    except Exception as e:
        print(f"   Failed: {e}")

    print("\n8. Stopping Trading Engine...")
    try:
        r = requests.post(f"{BASE_URL}/market/stop", headers=headers)
        print(f"   Response: {r.json()}")
    except Exception as e:
        print(f"   Failed: {e}")

if __name__ == "__main__":
    run_test()
