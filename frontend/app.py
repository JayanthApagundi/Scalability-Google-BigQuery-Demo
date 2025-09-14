from flask import Flask, render_template, jsonify, request
import requests
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for thread-safe plotting
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Backend services
BACKENDS = [
    "http://127.0.0.1:8000",  # Primary backend
    "http://127.0.0.1:8001",  # Secondary backend
    "http://127.0.0.1:8002",   # Tertiary backend
]

def fetch_data_with_failover(endpoint):
    """Fetch data from backend services with failover."""
    for service in BACKENDS:
        try:
            print(f"Trying {service}{endpoint}...")
            response = requests.get(f"{service}{endpoint}", timeout=100)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Non-200 response from {service}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to {service}: {e}")
    return {"error": "All backend services are unavailable. Please check server logs."}

@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')

@app.route('/scalability')
def scalability():
    """Render the scalability metrics page."""
    data = fetch_data_with_failover("/scalability/")
    if "error" in data:
        return render_template('scalability.html', data={"error": data["error"]})
    return render_template('scalability.html', data=data)

@app.route('/load_simulation')
def load_simulation():
    """Render the load simulation results page."""
    data = fetch_data_with_failover("/simulation_results/")  # Correct endpoint here

    # Generate a bar chart if data exists
    if "results" in data:
        user_ids = [res['user_id'] for res in data["results"] if 'response_time' in res]
        response_times = [res['response_time'] for res in data["results"] if 'response_time' in res]

        # Generate chart only if valid response times exist
        if user_ids and response_times:
            plt.figure(figsize=(10, 6))
            plt.bar(user_ids, response_times, color='skyblue')
            plt.xlabel("User ID")
            plt.ylabel("Response Time (s)")
            plt.title("Load Simulation Response Times")
            plt.tight_layout()

            # Save the chart to a BytesIO buffer
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            chart_url = base64.b64encode(img_buffer.read()).decode()

            return render_template('simulation_results.html', data=data, chart_url=chart_url)

    # If no results found or invalid data
    return render_template('simulation_results.html', data={"error": "No simulation data found"})

@app.route('/query_simulation')
def query_simulation():
    """Render query simulation results."""
    data = fetch_data_with_failover("/get_query_simulation_results/")
    if "error" in data:
        return render_template("query_simulation_results.html", data={"error": data["error"]})

    # Generate a bar chart for response times
    user_ids = [f"User {item['user_id']}" for item in data["results"]]
    response_times = [sum(q.get('response_time', 0) for q in item['queries']) for item in data["results"]]

    # Create bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(user_ids, response_times, color='skyblue')
    plt.xlabel("User ID")
    plt.ylabel("Total Response Time (s)")
    plt.title("Query Simulation Results")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Convert chart to base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.read()).decode()

    return render_template("query_simulation_results.html", data=data, chart_url=chart_url)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
