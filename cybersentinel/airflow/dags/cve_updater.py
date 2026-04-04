"""
TICKET-021 — CVE Knowledge Updater DAG.
Runs nightly at 2 AM to fetch new CVEs from NVD API,
parse them, embed them, upsert to ChromaDB, and validate ingestion.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

default_args = {
    "owner": "cybersentinel",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


def fetch_new_cves(**context):
    """Fetch CVEs published in last 24hrs from NVD API."""
    from airflow.tasks.fetch_cves import fetch_cves
    return fetch_cves()


def parse_and_clean_cves(**context):
    """Parse and clean raw CVE JSON into structured records."""
    from airflow.tasks.parse_cves import parse_cves
    raw = context["ti"].xcom_pull(task_ids="fetch_new_cves")
    return parse_cves(raw)


def generate_embeddings_task(**context):
    """Generate embeddings for parsed CVE records."""
    from airflow.tasks.embed_cves import embed_cves
    parsed = context["ti"].xcom_pull(task_ids="parse_and_clean")
    return embed_cves(parsed)


def upsert_chromadb_task(**context):
    """Upsert embedded CVE records into ChromaDB."""
    from airflow.tasks.embed_cves import upsert_to_chromadb
    embedded = context["ti"].xcom_pull(task_ids="generate_embeddings")
    return upsert_to_chromadb(embedded)


def validate_ingestion_task(**context):
    """Run test similarity query to confirm new CVEs are retrievable."""
    from airflow.tasks.validate_ingestion import validate
    return validate()


with DAG(
    dag_id="cve_knowledge_updater",
    description="Nightly CVE fetch, parse, embed, and upsert to ChromaDB",
    schedule="0 2 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    is_paused_upon_creation=False,
    tags=["cybersentinel", "cve", "rag"],
) as dag:

    fetch = PythonOperator(
        task_id="fetch_new_cves",
        python_callable=fetch_new_cves,
    )

    parse = PythonOperator(
        task_id="parse_and_clean",
        python_callable=parse_and_clean_cves,
    )

    embed = PythonOperator(
        task_id="generate_embeddings",
        python_callable=generate_embeddings_task,
    )

    upsert = PythonOperator(
        task_id="upsert_chromadb",
        python_callable=upsert_chromadb_task,
    )

    validate = PythonOperator(
        task_id="validate_ingestion",
        python_callable=validate_ingestion_task,
    )

    fetch >> parse >> embed >> upsert >> validate
