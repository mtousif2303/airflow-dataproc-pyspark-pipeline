# airflow-dataproc-pyspark-pipeline
This project demonstrates how to orchestrate PySpark batch jobs on Google Cloud Dataproc using Apache Airflow (Cloud Composer).
# Airflow Dataproc PySpark Pipeline

## 📌 Overview
This project demonstrates how to orchestrate **PySpark batch jobs on Google Cloud Dataproc** using **Apache Airflow (Cloud Composer)**.

The pipeline dynamically:
- Creates a Dataproc cluster
- Submits a PySpark job
- Deletes the cluster after execution

This approach ensures **cost efficiency**, **scalability**, and **production-grade orchestration**.

---

## 🏗 Architecture

Airflow (Cloud Composer)  
→ Dataproc Cluster (On-Demand)  
→ PySpark Job  
→ Google Cloud Storage (GCS)

---

## 🛠 Tech Stack

- Apache Airflow (Cloud Composer)
- Google Cloud Dataproc
- Apache Spark (PySpark)
- Google Cloud Storage (GCS)
- Python 3

---

## 📂 Project Structure

├── dags/
│ └── airflow_spark_job.py
├── spark-job/
│ └── emp_batch_job.py
├── data/
│ └── employee.csv


---

## ⚙️ Workflow Description

### 1. Create Dataproc Cluster
- Uses `DataprocCreateClusterOperator`
- Provisions cluster on demand

### 2. Submit PySpark Job
- Reads CSV data from GCS
- Performs Spark transformations

### 3. Delete Dataproc Cluster
- Ensures cluster cleanup using `trigger_rule='all_done'`

---

## ▶️ How to Run

### Prerequisites
- Google Cloud Project
- Cloud Composer environment
- Dataproc API enabled
- GCS bucket for Spark jobs and data

---

### Step 1: Upload DAG

```bash
gsutil cp dags/airflow_spark_job.py gs://<COMPOSER_BUCKET>/dags/

Step 2: Upload PySpark Job
gsutil cp spark-job/emp_batch_job.py gs://<GCS_BUCKET>/spark-job/
Step 3: Upload Input Data
gsutil cp data/employee.csv gs://<GCS_BUCKET>/data/
Step 4: Trigger DAG
Open Airflow UI

Trigger adhoc_spark_job_on_dataproc

✅ Best Practices Implemented

On-demand Dataproc clusters for cost optimization

Automatic cluster cleanup

Cloud-native storage using GCS

Clear separation of orchestration and processing

Production-ready Airflow operators

🚀 Future Enhancements

Parameterized Spark job inputs

Logging and monitoring

Delta Lake integration

CI/CD pipeline for DAG deployment

Unit testing for PySpark jobs
