from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitJobOperator,
    DataprocDeleteClusterOperator,
)

# -----------------------------
# Default arguments
# -----------------------------
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# -----------------------------
# DAG definition
# -----------------------------
with DAG(
    dag_id='adhoc_spark_job_on_dataproc',
    description='A DAG to setup Dataproc cluster and run a PySpark job',
    start_date=datetime(2024, 12, 14),
    schedule=None,           # Manual / on-demand
    catchup=False,
    tags=['dev'],
    default_args=default_args,
) as dag:

    # -----------------------------
    # Cluster configuration
    # -----------------------------
    CLUSTER_NAME = 'dataproc-spark-airflow-demo'
    PROJECT_ID = 'third-extension-477605-j1'
    REGION = 'us-central1'

    CLUSTER_CONFIG = {
        'master_config': {
            'num_instances': 1,
            'machine_type_uri': 'n1-standard-2',
            'disk_config': {
                'boot_disk_type': 'pd-standard',
                'boot_disk_size_gb': 30,
            },
        },
        'worker_config': {
            'num_instances': 2,
            'machine_type_uri': 'n1-standard-2',
            'disk_config': {
                'boot_disk_type': 'pd-standard',
                'boot_disk_size_gb': 30,
            },
        },
        'software_config': {
            'image_version': '2.2.26-debian12',
        },
    }

    # -----------------------------
    # Tasks
    # -----------------------------
    create_cluster = DataprocCreateClusterOperator(
        task_id='create_dataproc_cluster',
        project_id=PROJECT_ID,
        region=REGION,
        cluster_name=CLUSTER_NAME,
        cluster_config=CLUSTER_CONFIG,
    )

    submit_pyspark_job = DataprocSubmitJobOperator(
        task_id='submit_pyspark_job_on_dataproc',
        project_id=PROJECT_ID,
        region=REGION,
        job={
            "placement": {
                "cluster_name": CLUSTER_NAME
            },
            "pyspark_job": {
                "main_python_file_uri": (
                    "gs://airflow-projects-de/airflow-project-01/"
                    "spark-job/emp_batch_job.py"
                )
            },
        },
    )

    delete_cluster = DataprocDeleteClusterOperator(
        task_id='delete_dataproc_cluster',
        project_id=PROJECT_ID,
        region=REGION,
        cluster_name=CLUSTER_NAME,
        trigger_rule='all_done',  # ALWAYS delete cluster
    )

    # -----------------------------
    # Dependencies
    # -----------------------------
    create_cluster >> submit_pyspark_job >> delete_cluster
