import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

API_URL = "http://127.0.0.1:8000/save_query_simulation_results/"  # Django Backend API URL
QUERY_EXECUTION_URL = "http://127.0.0.1:8000/execute_bigquery/"# Django Backend endpoint

# Define query sets (4 queries per set)
QUERY_SETS = [
     # Set 1
    [
        "SELECT traffic_source, COUNT(*) AS clicks FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY traffic_source;",
        "SELECT session_id, MIN(event_time) AS start_time, MAX(event_time) AS end_time FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY session_id;",
        "SELECT home_country, COUNT(customer_id) AS total_customers FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY home_country;",
        "SELECT gender, COUNT(*) AS total_purchases FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY gender;"
    ],
    # Set 2
    [
        "SELECT COUNT(DISTINCT session_id) AS unique_sessions FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream`;",
        "SELECT event_name, COUNT(event_id) AS total_events FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY event_name;",
        "SELECT gender, SUM(total_amount) AS revenue FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY gender;",
        "SELECT home_country, gender, COUNT(customer_id) AS customer_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY home_country, gender;"
    ],
    # Set 3
    [
        "SELECT session_id, TIMESTAMP_DIFF(MAX(event_time), MIN(event_time), SECOND) AS session_duration FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY session_id;",
        "SELECT productDisplayName, COUNT(*) AS total_products FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_product` GROUP BY productDisplayName;",
        "SELECT traffic_source, COUNT(session_id) AS session_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY traffic_source;",
        "SELECT home_country, COUNT(customer_id) AS customer_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY home_country;"
    ],
    # Set 4
    [
        "SELECT gender, COUNT(*) AS total_customers FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY gender;",
        "SELECT articleType, COUNT(*) AS product_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_product` GROUP BY articleType;",
        "SELECT event_name, COUNT(DISTINCT session_id) AS unique_sessions FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY event_name;",
        "SELECT booking_id, SUM(total_amount) AS total_revenue FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY booking_id;"
    ],
    # Set 5
    [
        "SELECT COUNT(*) AS total_sessions FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream`;",
        "SELECT COUNT(event_id) AS total_events, event_name FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY event_name;",
        "SELECT promo_code, SUM(total_amount) AS total_discount FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY promo_code;",
        "SELECT home_country, COUNT(DISTINCT customer_id) AS unique_customers FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY home_country;"
    ],
    # Set 6
    [
        "SELECT COUNT(*) AS click_count, traffic_source FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY traffic_source;",
        "SELECT baseColour, COUNT(*) AS colour_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_product` GROUP BY baseColour;",
        "SELECT payment_status, COUNT(*) AS payment_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY payment_status;",
        "SELECT device_type, COUNT(*) AS device_usage FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY device_type;"
    ],
    # Set 7
    [
        "SELECT COUNT(*) AS cart_abandonments FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` WHERE event_name = 'cart_abandonment';",
        "SELECT COUNT(DISTINCT customer_id) AS total_customers FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer`;",
        "SELECT traffic_source, SUM(total_amount) AS total_revenue FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY traffic_source;",
        "SELECT session_id, COUNT(event_id) AS total_events FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY session_id;"
    ],
    # Set 8
    [
        "SELECT COUNT(DISTINCT session_id) AS active_sessions FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream`;",
        "SELECT COUNT(*) AS total_products, masterCategory FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_product` GROUP BY masterCategory;",
        "SELECT home_country, gender, COUNT(customer_id) AS customers FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY home_country, gender;",
        "SELECT session_id, COUNT(event_id) AS total_events FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY session_id;"
    ],
    # Set 9
    [
        "SELECT COUNT(*) AS successful_payments FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` WHERE payment_status = 'Completed';",
        "SELECT COUNT(event_id) AS events, traffic_source FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY traffic_source;",
        "SELECT gender, SUM(total_amount) AS revenue FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY gender;",
        "SELECT year, COUNT(*) AS total_products FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_product` GROUP BY year;"
    ],
    # Set 10
    [
        "SELECT session_id, COUNT(event_id) AS event_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY session_id;",
        "SELECT COUNT(DISTINCT booking_id) AS purchases FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions`;",
        "SELECT traffic_source, COUNT(session_id) AS sessions FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY traffic_source;",
        "SELECT articleType, COUNT(*) AS product_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_product` GROUP BY articleType;"
    ],
   # Set 11
    [
        "SELECT traffic_source, COUNT(DISTINCT session_id) AS unique_sessions FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY traffic_source;",
        "SELECT home_country, SUM(total_amount) AS total_revenue FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY home_country;",
        "SELECT device_type, COUNT(customer_id) AS device_usage FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY device_type;",
        "SELECT gender, COUNT(customer_id) AS total_customers FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY gender;"
    ],
    # Set 12
    [
        "SELECT year, COUNT(*) AS total_products FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_product` GROUP BY year;",
        "SELECT payment_status, SUM(total_amount) AS total_value FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY payment_status;",
        "SELECT session_id, MIN(event_time) AS session_start, MAX(event_time) AS session_end FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY session_id;",
        "SELECT gender, COUNT(*) AS total_users FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY gender;"
    ],
    # Set 13
    [
        "SELECT articleType, COUNT(*) AS product_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_product` GROUP BY articleType;",
        "SELECT COUNT(DISTINCT session_id) AS total_sessions FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream`;",
        "SELECT home_country, COUNT(customer_id) AS customer_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY home_country;",
        "SELECT traffic_source, COUNT(event_id) AS event_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY traffic_source;"
    ],
    # Set 14
    [
        "SELECT promo_code, COUNT(booking_id) AS total_transactions FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY promo_code;",
        "SELECT masterCategory, COUNT(*) AS category_products FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_product` GROUP BY masterCategory;",
        "SELECT event_name, COUNT(event_id) AS total_events FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY event_name;",
        "SELECT home_country, gender, COUNT(customer_id) AS customer_distribution FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY home_country, gender;"
    ],
    # Set 15
    [
        "SELECT payment_status, COUNT(*) AS total_payments FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY payment_status;",
        "SELECT baseColour, COUNT(*) AS color_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_product` GROUP BY baseColour;",
        "SELECT traffic_source, COUNT(session_id) AS session_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY traffic_source;",
        "SELECT gender, SUM(total_amount) AS total_revenue FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY gender;"
    ],
    # Set 16
    [
        "SELECT device_version, COUNT(*) AS device_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY device_version;",
        "SELECT COUNT(DISTINCT session_id) AS total_active_sessions FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream`;",
        "SELECT traffic_source, SUM(total_amount) AS revenue_generated FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY traffic_source;",
        "SELECT home_country, COUNT(customer_id) AS customer_base FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY home_country;"
    ],
    # Set 17
    [
        "SELECT gender, COUNT(customer_id) AS user_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY gender;",
        "SELECT productDisplayName, COUNT(*) AS product_sales FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_product` GROUP BY productDisplayName;",
        "SELECT event_name, COUNT(DISTINCT session_id) AS unique_sessions FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY event_name;",
        "SELECT booking_id, SUM(total_amount) AS revenue FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY booking_id;"
    ],
    # Set 18
    [
        "SELECT COUNT(DISTINCT session_id) AS session_count, traffic_source FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY traffic_source;",
        "SELECT COUNT(event_id) AS total_events FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream`;",
        "SELECT gender, COUNT(DISTINCT customer_id) AS customer_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY gender;",
        "SELECT home_country, SUM(total_amount) AS total_revenue FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY home_country;"
    ],
    # Set 19
    [
        "SELECT device_type, COUNT(*) AS total_devices FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` GROUP BY device_type;",
        "SELECT year, COUNT(*) AS product_count FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_product` GROUP BY year;",
        "SELECT event_name, COUNT(event_id) AS total_clicks FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY event_name;",
        "SELECT traffic_source, COUNT(DISTINCT session_id) AS active_sessions FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` GROUP BY traffic_source;"
    ],
    # Set 20
    [
        "SELECT COUNT(session_id) AS abandoned_sessions FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` WHERE event_name = 'cart_abandonment';",
        "SELECT gender, SUM(total_amount) AS gender_revenue FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY gender;",
        "SELECT masterCategory, COUNT(*) AS total_products FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_product` GROUP BY masterCategory;",
        "SELECT traffic_source, SUM(total_amount) AS revenue FROM `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` GROUP BY traffic_source;"
    ]

]

def simulate_queries(user_id, query_set):
    results = {"user_id": user_id, "queries": []}
    for query in query_set:
        try:
            response = requests.post(
                QUERY_EXECUTION_URL,
                json={"query": query},
                timeout=300
            )
            if response.status_code == 200:
                results["queries"].append({"query": query, "status": "success", "response_time": response.json().get("response_time", 0)})
            else:
                results["queries"].append({"query": query, "error": response.text})
        except Exception as e:
            results["queries"].append({"query": query, "error": str(e)})
    return results

def simulate_user_load(num_users=20):
    results = []
    with ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(simulate_queries, user_id=i, query_set=random.choice(QUERY_SETS)) for i in range(1, num_users + 1)]
        for future in as_completed(futures):
            results.append(future.result())

    # Send results to the backend
    try:
        response = requests.post(API_URL, json={"simulation_results": results, "num_users": num_users})
        print("Results stored:", response.json())
    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == "__main__":
    print("Starting query simulation...")
    simulate_user_load(20)