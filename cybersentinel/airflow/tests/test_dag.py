"""
TICKET-021 — Airflow DAG structure tests.
Tests DAG importability, task existence, and dependency ordering
without requiring a running Airflow instance.
"""
import pytest
from unittest.mock import patch, MagicMock


# ── Helpers ───────────────────────────────────────────────────────────────────

def import_dag():
    """Import the DAG module and return the dag object."""
    from airflow.dags.cve_updater import dag
    return dag


# ── DAG structure tests ───────────────────────────────────────────────────────

class TestCVEUpdaterDAGImport:

    def test_dag_imports_without_error(self):
        dag = import_dag()
        assert dag is not None

    def test_dag_id_is_correct(self):
        dag = import_dag()
        assert dag.dag_id == "cve_knowledge_updater"

    def test_dag_has_correct_schedule(self):
        dag = import_dag()
        # Nightly at 2 AM
        assert dag.schedule == "0 2 * * *"

    def test_dag_is_not_paused_on_creation(self):
        dag = import_dag()
        assert dag.is_paused_upon_creation is False


class TestCVEUpdaterDAGTasks:

    def test_dag_has_five_tasks(self):
        dag = import_dag()
        assert len(dag.tasks) == 5

    def test_dag_has_fetch_cves_task(self):
        dag = import_dag()
        task_ids = [t.task_id for t in dag.tasks]
        assert "fetch_new_cves" in task_ids

    def test_dag_has_parse_task(self):
        dag = import_dag()
        task_ids = [t.task_id for t in dag.tasks]
        assert "parse_and_clean" in task_ids

    def test_dag_has_embed_task(self):
        dag = import_dag()
        task_ids = [t.task_id for t in dag.tasks]
        assert "generate_embeddings" in task_ids

    def test_dag_has_upsert_task(self):
        dag = import_dag()
        task_ids = [t.task_id for t in dag.tasks]
        assert "upsert_chromadb" in task_ids

    def test_dag_has_validate_task(self):
        dag = import_dag()
        task_ids = [t.task_id for t in dag.tasks]
        assert "validate_ingestion" in task_ids


class TestCVEUpdaterDAGDependencies:

    def test_fetch_runs_before_parse(self):
        dag = import_dag()
        fetch = dag.get_task("fetch_new_cves")
        parse = dag.get_task("parse_and_clean")
        assert parse.task_id in [t.task_id for t in fetch.downstream_list]

    def test_parse_runs_before_embed(self):
        dag = import_dag()
        parse = dag.get_task("parse_and_clean")
        embed = dag.get_task("generate_embeddings")
        assert embed.task_id in [t.task_id for t in parse.downstream_list]

    def test_embed_runs_before_upsert(self):
        dag = import_dag()
        embed = dag.get_task("generate_embeddings")
        upsert = dag.get_task("upsert_chromadb")
        assert upsert.task_id in [t.task_id for t in embed.downstream_list]

    def test_upsert_runs_before_validate(self):
        dag = import_dag()
        upsert = dag.get_task("upsert_chromadb")
        validate = dag.get_task("validate_ingestion")
        assert validate.task_id in [t.task_id for t in upsert.downstream_list]

    def test_fetch_has_no_upstream(self):
        dag = import_dag()
        fetch = dag.get_task("fetch_new_cves")
        assert len(fetch.upstream_list) == 0

    def test_validate_has_no_downstream(self):
        dag = import_dag()
        validate = dag.get_task("validate_ingestion")
        assert len(validate.downstream_list) == 0
