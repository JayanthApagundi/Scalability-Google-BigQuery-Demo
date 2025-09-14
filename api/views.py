from concurrent.futures import ThreadPoolExecutor, as_completed
import random
from venv import logger
from django.http import JsonResponse
from flask import request
from google.cloud import bigquery
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

client = bigquery.Client()

# Global storage for query simulation results
QUERY_SIMULATION_RESULTS = {"results": [], "num_users": 0}

@csrf_exempt
def execute_bigquery(request):
    """Execute a BigQuery query and return the execution time."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            query = data.get("query")
            if not query:
                return JsonResponse({"error": "No query provided"}, status=400)

            # Measure query execution time
            start_time = time.time()
            job_config = bigquery.QueryJobConfig(use_query_cache=False)
            query_job = client.query(query, job_config=job_config)
            query_job.result()  # Trigger execution
            execution_time = round((time.time() - start_time), 2)

            return JsonResponse({"response_time": execution_time})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def save_query_simulation_results(request):
    """Save the query simulation results."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            QUERY_SIMULATION_RESULTS["results"] = data.get("simulation_results", [])
            QUERY_SIMULATION_RESULTS["num_users"] = data.get("num_users", 0)
            return JsonResponse({"status": "success", "message": "Results saved successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

def get_query_simulation_results(request):
    """Return saved query simulation results."""
    return JsonResponse(QUERY_SIMULATION_RESULTS, safe=False)

# Global variable to store load simulation results
LOAD_SIMULATION_RESULTS = {"results": [], "num_users": 0}

@csrf_exempt
def save_simulation_results(request):
    """
    Receive and save load simulation results (POST).
    Endpoint: /save_simulation_results/
    """
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            LOAD_SIMULATION_RESULTS["results"] = data.get("simulation_results", [])
            LOAD_SIMULATION_RESULTS["num_users"] = data.get("num_users", 0)
            return JsonResponse({"status": "success", "message": "Results stored successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)


def get_simulation_results(request):
    """
    Retrieve stored load simulation results (GET).
    Endpoint: /simulation_results/
    """
    return JsonResponse(LOAD_SIMULATION_RESULTS, safe=False)

def execute_query_with_stages(query):
    """Execute a BigQuery query and collect execution metrics, including stage details."""
    try:
        start_time = time.time()
        job_config = bigquery.QueryJobConfig(use_query_cache=False)  # Ensure fresh execution
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # Trigger query execution and wait

        execution_time = (time.time() - start_time) * 1000  # ms

        # Safely handle query plan
        stages = []
        if query_job.query_plan:
            for stage in query_job.query_plan:
                stages.append({
                    "stage_name": stage.name if stage.name else "N/A",
                    "records_read": stage.records_read if stage.records_read else 0,
                    "records_written": stage.records_written if stage.records_written else 0,
                    "wait_time": round(stage.wait_ratio_avg * 1000, 2) if stage.wait_ratio_avg else 0,
                    "read_time": round(stage.read_ratio_avg * 1000, 2) if stage.read_ratio_avg else 0,
                    "compute_time": round(stage.compute_ratio_avg * 1000, 2) if stage.compute_ratio_avg else 0,
                    "write_time": round(stage.write_ratio_avg * 1000, 2) if stage.write_ratio_avg else 0,
                })
        else:
            stages.append({"stage_name": "N/A", "error": "No execution stages available"})

        return None, {
            "execution_time_ms": round(execution_time, 2),
            "total_bytes_processed": query_job.total_bytes_processed or 0,
            "slot_time_sec": round(query_job.slot_millis / 1000, 2) if query_job.slot_millis else 0,
            "stages": stages
        }

    except Exception as e:
        return None, {"error": str(e)}

def scalability_results(request):
    """Fetch all query results and their execution times."""
    queries = {
        "Top Traffic Sources with Session-Based Revenue and Event Counts": """
        SELECT 
            c.traffic_source,
            COUNT(DISTINCT c.session_id) AS total_sessions,
            COUNT(c.event_id) AS total_events,
            SUM(t.total_amount) AS total_revenue
        FROM 
            `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` c
        LEFT JOIN 
            `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` t
        ON 
            c.session_id = t.session_id
        GROUP BY 
            c.traffic_source
        ORDER BY 
            total_revenue DESC, total_sessions DESC;
        """,
        "Session Duration Analysis": """
            SELECT 
            session_id,
            MIN(event_time) AS session_start,
            MAX(event_time) AS session_end,
            TIMESTAMP_DIFF(MAX(event_time), MIN(event_time), SECOND) AS session_duration_sec
        FROM 
            `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream`
        GROUP BY 
            session_id
        ORDER BY 
            session_duration_sec DESC
        LIMIT 10;
        """,
        "Conversion Rate by Traffic Source":"""
            WITH session_counts AS (
                SELECT 
                    traffic_source,
                    COUNT(DISTINCT session_id) AS total_sessions
                FROM 
                    `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream`
                GROUP BY traffic_source
            ),
            conversion_counts AS (
                SELECT 
                    c.traffic_source,
                    COUNT(DISTINCT t.booking_id) AS total_purchases
                FROM 
                    `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` c
                JOIN 
                    `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` t
                ON 
                    c.session_id = t.session_id
                WHERE 
                    t.payment_status = 'Completed'
                GROUP BY c.traffic_source
            )
            SELECT 
                sc.traffic_source,
                sc.total_sessions,
                cc.total_purchases,
                ROUND((cc.total_purchases / sc.total_sessions) * 100, 2) AS conversion_rate_percentage
            FROM 
                session_counts sc
            JOIN 
                conversion_counts cc
            ON 
                sc.traffic_source = cc.traffic_source
            ORDER BY 
                conversion_rate_percentage DESC;
        """,
        "Traffic Source Analysis":"""
            SELECT 
            traffic_source,
            COUNT(*) AS clicks
            FROM 
            `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream`
            GROUP BY 
            traffic_source
            ORDER BY 
            clicks DESC;
        """,
        "Longest Sessions with High Event Activity":""" 
            SELECT 
                session_id,
                MIN(event_time) AS session_start,
                MAX(event_time) AS session_end,
                COUNT(event_id) AS total_events,
                TIMESTAMP_DIFF(MAX(event_time), MIN(event_time), SECOND) AS session_duration_sec
            FROM 
                `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream`
            GROUP BY 
                session_id
            HAVING 
                session_duration_sec > 0
            ORDER BY 
                session_duration_sec DESC, total_events DESC
            LIMIT 50;
        """,
        "Customer Purchase Behavior Across Regions":"""
            SELECT 
                cu.home_country,
                cu.gender,
                COUNT(t.booking_id) AS total_transactions,
                SUM(t.total_amount) AS total_sales
            FROM 
                `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` t
            JOIN 
                `spheric-camera-444321-g6.ecommerce_data.ecommerce_customer` cu
            ON 
                t.customer_id = cu.customer_id
            GROUP BY 
                cu.home_country, cu.gender
            ORDER BY 
                total_sales DESC;
        """,
        "User Journey Analysis with Revenue Contribution by Event Type":""" 
            WITH user_event_sessions AS (
                SELECT 
                    c.event_name,
                    c.session_id,
                    COUNT(c.event_id) AS total_events,
                    COUNT(t.booking_id) AS total_purchases,
                    SUM(t.total_amount) AS total_revenue
                FROM 
                    `spheric-camera-444321-g6.ecommerce_data.ecommerce_click_stream` c
                LEFT JOIN 
                    `spheric-camera-444321-g6.ecommerce_data.ecommerce_transactions` t
                ON 
                    c.session_id = t.session_id
                    AND t.payment_status = 'Completed'
                GROUP BY 
                    c.event_name, c.session_id
            ),
            aggregated_user_journey AS (
                SELECT 
                    event_name,
                    COUNT(DISTINCT session_id) AS total_sessions,
                    SUM(total_events) AS total_event_count,
                    SUM(total_purchases) AS total_purchases,
                    SUM(total_revenue) AS total_revenue
                FROM 
                    user_event_sessions
                GROUP BY 
                    event_name
            )
            SELECT 
                event_name,
                total_sessions,
                total_event_count,
                total_purchases,
                total_revenue,
                ROUND(total_revenue / NULLIF(total_purchases, 0), 2) AS avg_revenue_per_purchase
            FROM 
                aggregated_user_journey
            ORDER BY 
                total_revenue DESC, total_sessions DESC
            LIMIT 50;
            """,
    }

    results = {}
    for query_name, query in queries.items():
        _, metrics = execute_query_with_stages(query)
        results[query_name] = metrics

    return JsonResponse(results, safe=False)