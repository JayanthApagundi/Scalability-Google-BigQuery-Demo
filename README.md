
# Distributed Systems Design – Scalability Focus  

This project demonstrates **scalability in distributed systems** using a Django backend, a lightweight frontend, and integration with **Google BigQuery** for large-scale data analytics. The goal of this project is to showcase how systems can be designed to **scale horizontally and vertically** to handle increasing workloads, larger datasets, and higher numbers of users.  

---

## 🚀 Key Idea: Scalability  

- **Horizontal Scaling** → Adding more nodes/servers to share the workload.  
- **Vertical Scaling** → Increasing resources (CPU, memory, etc.) on existing nodes.  
- **BigQuery Integration** → Demonstrates cloud-scale query execution and analytics.  
- **Synthetic Data Generation** → Creates large datasets to simulate real-world growth.  

---

## 🏗️ Project Structure  

│── backend/ # Django backend (API, models, scalability features) <br>
│── frontend/ # Flask/HTML frontend (UI templates, app.py) <br>
│── api/ # Django API logic <br>
│── db.sqlite3 # Local SQLite database <br>
│── bigquery_access.json # Google BigQuery credentials (ignored in Git) <br>
│── synthetic_data.py # Script to generate synthetic data for scalability tests <br>
│── dataset.py # Dataset handling and preprocessing <br>
│── manage.py # Django management script <br>

## ⚙️ Installation & Setup  

### 1️⃣ Clone the repository  
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

cd backend
python manage.py runserver

cd frontend
python app.py

```

## Scalability Demonstrations
- Synthetic Data Growth → Generate increasingly larger datasets with synthetic_data.py to test system limits.
- BigQuery Analytics → Run queries on large-scale e-commerce data to demonstrate cloud-scale query handling.
- Frontend Scalability Page → UI includes a dedicated scalability.html page showing results and performance impact.

