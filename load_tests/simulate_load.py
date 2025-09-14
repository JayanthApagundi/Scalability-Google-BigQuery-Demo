import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

API_URL = "http://127.0.0.1:8000/save_simulation_results/"  # Django Backend API URL
FRONTEND_URL = "http://127.0.0.1:5000/scalability"          # Frontend Flask app

def make_request(user_id):
    try:
        start_time = time.time()
        response = requests.get(FRONTEND_URL, timeout=150)
        end_time = time.time()
        if response.status_code == 200:
            return {"user_id": user_id, "response_time": end_time - start_time, "status": "success"}
        else:
            return {"user_id": user_id, "error": f"Status Code: {response.status_code}"}
    except Exception as e:
        return {"user_id": user_id, "error": str(e)}

def simulate_user_load(num_users=10):
    results = []
    with ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(make_request, user_id=i) for i in range(1, num_users + 1)]
        for future in as_completed(futures):
            results.append(future.result())

    # Send results to Django API
    try:
        response = requests.post(API_URL, json={"simulation_results": results, "num_users": num_users})
        print("Results stored:", response.json())
    except Exception as e:
        print("Error sending simulation results:", e)
    return results

if __name__ == "__main__":
    NUM_USERS = 20
    print(f"Simulating {NUM_USERS} users...")
    simulate_user_load(NUM_USERS)
