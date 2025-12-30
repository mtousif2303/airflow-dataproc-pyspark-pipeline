# Airflow Dataproc PySpark Pipeline

## 📌 Overview

This project demonstrates a production-grade data engineering pipeline that orchestrates PySpark batch jobs on Google Cloud Dataproc using Apache Airflow (Cloud Composer). The pipeline processes employee and department data, performing filtering and join operations before writing results to Google Cloud Storage.

**Key Features:**
- Dynamic Dataproc cluster provisioning and teardown
- Cost-efficient ephemeral compute resources
- Automated workflow orchestration with Airflow
- Cloud-native data processing on GCP

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Apache Airflow                            │
│                  (Cloud Composer)                            │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│              Create Dataproc Cluster                         │
│           (1 Master + 2 Worker Nodes)                        │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                 Submit PySpark Job                           │
│    • Read employee.csv & department.csv from GCS             │
│    • Filter employees (salary > 50000)                       │
│    • Join with department data                               │
│    • Write results to GCS                                    │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│              Delete Dataproc Cluster                         │
│              (trigger_rule: all_done)                        │
└─────────────────────────────────────────────────────────────┘
```
adhoc_spark_job_on_dataproc

<img width="1728" height="1039" alt="image" src="https://github.com/user-attachments/assets/84ce84ac-2bfa-4be9-8de1-8f70843a323a" />

airflow_spark_job.py

<img width="1721" height="945" alt="image" src="https://github.com/user-attachments/assets/d7fdb3eb-8ae2-43c9-9143-0f32fee4814f" />


<img width="3426" height="1772" alt="image" src="https://github.com/user-attachments/assets/3286204f-4799-4f41-81cc-072bad5d282b" />




---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Apache Airflow** | Workflow orchestration and scheduling |
| **Google Cloud Composer** | Managed Airflow service |
| **Google Cloud Dataproc** | Managed Spark/Hadoop service |
| **Apache Spark (PySpark)** | Distributed data processing |
| **Google Cloud Storage** | Data lake storage |
| **Python 3** | Programming language |

---

## 📂 Project Structure

```
airflow-dataproc-pipeline/
│
├── dags/
│   └── airflow_spark_job.py          # Airflow DAG definition
│
├── spark-job/
│   └── emp_batch_job.py               # PySpark processing logic
│
├── data/
│   ├── employee.csv                   # Employee dataset
│   └── department.csv                 # Department dataset
│
├── output/                            # Processed data output (GCS)
│
└── README.md                          # Project documentation
```

---

## 📋 Prerequisites

Before running this pipeline, ensure you have:

1. **Google Cloud Project** with billing enabled
2. **APIs Enabled:**
   - Cloud Composer API
   - Dataproc API
   - Cloud Storage API
3. **GCS Bucket** created (e.g., `airflow-projects-de`)
4. **Cloud Composer Environment** set up
5. **Service Account** with appropriate permissions:
   - Dataproc Administrator
   - Storage Object Admin
   - Composer Worker

---

## ⚙️ Pipeline Workflow

### Task 1: Create Dataproc Cluster
```python
create_cluster = DataprocCreateClusterOperator(
    task_id='create_dataproc_cluster',
    cluster_name='dataproc-spark-airflow-demo',
    cluster_config={
        'master_config': {'num_instances': 1, 'machine_type_uri': 'n1-standard-2'},
        'worker_config': {'num_instances': 2, 'machine_type_uri': 'n1-standard-2'}
    }
)
```
**Purpose:** Provisions an ephemeral Dataproc cluster with 1 master and 2 worker nodes.

### Task 2: Submit PySpark Job
```python
submit_pyspark_job = DataprocSubmitJobOperator(
    task_id='submit_pyspark_job_on_dataproc',
    job={
        "pyspark_job": {
            "main_python_file_uri": "gs://airflow-projects-de/.../emp_batch_job.py"
        }
    }
)
```
**Purpose:** Executes the PySpark job that:
- Reads `employee.csv` and `department.csv` from GCS
- Filters employees with salary > $50,000
- Performs inner join on `dept_id`
- Writes results back to GCS in CSV format

### Task 3: Delete Dataproc Cluster
```python
delete_cluster = DataprocDeleteClusterOperator(
    task_id='delete_dataproc_cluster',
    trigger_rule='all_done'  # Ensures cleanup even if job fails
)
```
**Purpose:** Tears down the cluster to avoid unnecessary costs.

---

## 🚀 Deployment Instructions

### Step 1: Set Up GCP Environment

```bash
# Set your GCP project
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export BUCKET_NAME="airflow-projects-de"

# Create GCS bucket (if not exists)
gsutil mb -p $PROJECT_ID -l $REGION gs://$BUCKET_NAME
```

### Step 2: Upload Data Files

```bash
# Upload employee data
gsutil cp data/employee.csv gs://$BUCKET_NAME/airflow-project-01/data/

# Upload department data
gsutil cp data/department.csv gs://$BUCKET_NAME/airflow-project-01/data/
```

### Step 3: Upload PySpark Job

```bash
# Upload the Spark processing script
gsutil cp spark-job/emp_batch_job.py gs://$BUCKET_NAME/airflow-project-01/spark-job/
```

### Step 4: Deploy Airflow DAG

```bash
# Get your Composer bucket name
export COMPOSER_BUCKET=$(gcloud composer environments describe YOUR_COMPOSER_ENV \
    --location $REGION \
    --format="get(config.dagGcsPrefix)")

# Upload DAG file
gsutil cp dags/airflow_spark_job.py $COMPOSER_BUCKET/
```

### Step 5: Trigger the Pipeline

1. Navigate to **Cloud Composer** in GCP Console
2. Open the **Airflow UI**
3. Locate the DAG: `adhoc_spark_job_on_dataproc`
4. Click the **Play button** to trigger manually
5. Monitor execution in the **Graph View**

---

## 📊 Data Processing Logic

The PySpark job performs the following transformations:

```python
# 1. Read data from GCS
employee = spark.read.csv("gs://.../employee.csv", header=True, inferSchema=True)
department = spark.read.csv("gs://.../department.csv", header=True, inferSchema=True)

# 2. Filter employees
filtered_employee = employee.filter(employee.salary > 50000)

# 3. Join datasets
joined_data = filtered_employee.join(department, "dept_id", "inner")

# 4. Write output
joined_data.write.csv("gs://.../output", mode="overwrite", header=True)
```

**Sample Input (employee.csv):**
```
emp_id,name,dept_id,salary
1,John Doe,101,60000
2,Jane Smith,102,45000
3,Bob Johnson,101,75000
```

**Sample Output (joined data):**
```
emp_id,name,dept_id,salary,dept_name
1,John Doe,101,60000,Engineering
3,Bob Johnson,101,75000,Engineering
```

---

## 🔍 Monitoring and Troubleshooting

### View Airflow Logs
1. Open **Airflow UI** from Cloud Composer
2. Click on the task (e.g., `submit_pyspark_job_on_dataproc`)
3. Select **Log** tab

### View Dataproc Job Logs
```bash
gcloud dataproc jobs list --region=$REGION

gcloud dataproc jobs describe JOB_ID --region=$REGION
```

### Common Issues

| Issue | Solution |
|-------|----------|
| **Permission Denied** | Ensure service account has `roles/dataproc.admin` and `roles/storage.objectAdmin` |
| **Cluster Creation Timeout** | Check quota limits in GCP or increase `retry_delay` |
| **File Not Found** | Verify GCS paths in `emp_batch_job.py` are correct |
| **PySpark Job Fails** | Check YARN logs in Dataproc job details |

---

## 💰 Cost Optimization

This pipeline implements several cost-saving measures:

- **Ephemeral Clusters:** Dataproc clusters are created only when needed and deleted after job completion
- **Preemptible Workers:** Can be configured to use preemptible VMs for 80% cost savings
- **Right-sized Resources:** Uses `n1-standard-2` machines appropriate for the workload
- **Trigger Rule:** `all_done` ensures cluster cleanup even if job fails

**Estimated Cost per Run:** ~$0.10 - $0.20 (depends on data size and execution time)

---

## ✅ Best Practices Implemented

- **Infrastructure as Code:** Cluster configuration defined in Python
- **Idempotency:** DAG can be safely re-run without side effects
- **Error Handling:** `trigger_rule='all_done'` ensures cleanup
- **Separation of Concerns:** Orchestration (Airflow) vs Processing (Spark)
- **Cloud-Native Design:** Leverages managed services (Composer, Dataproc, GCS)
- **Observability:** Comprehensive logging at each stage

---

## 🎯 Future Enhancements

- [ ] Add data quality checks with Great Expectations
- [ ] Implement incremental processing with partitioned data
- [ ] Add Slack/email notifications for job failures
- [ ] Parameterize DAG with Airflow Variables
- [ ] Integrate with BigQuery for analytics
- [ ] Add unit tests for PySpark transformations
- [ ] Implement CI/CD pipeline with Cloud Build
- [ ] Add data lineage tracking with DataHub or Apache Atlas
- [ ] Migrate to Delta Lake for ACID transactions
- [ ] Add monitoring dashboards with Cloud Monitoring

---

## 📚 Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Cloud Dataproc Documentation](https://cloud.google.com/dataproc/docs)
- [PySpark API Reference](https://spark.apache.org/docs/latest/api/python/)
- [Cloud Composer Best Practices](https://cloud.google.com/composer/docs/best-practices)

---


---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⭐ Acknowledgments

This project demonstrates real-world data engineering capabilities including:
- Workflow orchestration with Apache Airflow
- Distributed data processing using Apache Spark
- Cloud-native architecture on Google Cloud Platform
- Cost-efficient batch processing pipelines
- Production-ready DevOps practices

**If you found this project helpful, please consider giving it a star! ⭐**
