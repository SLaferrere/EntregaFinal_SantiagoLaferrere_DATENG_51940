from datetime import datetime
from datetime import timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.models.param import Param
from airflow.operators.python_operator import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


defaul_args = {
    "owner": "Santiago Laferrere",
    "start_date": datetime(2023, 7, 18),
    "retries": 0,
    "retry_delay": timedelta(seconds=5),
}

with DAG(
    dag_id="etl_users",
    default_args=defaul_args,
    description="ETL de la tabla usersinformation",
    schedule_interval="@daily",
    catchup=False,
    params={
        "process_date": Param(
            datetime.now().strftime("%Y-%m-%d"), type="string", title="date"
        ),
    },
) as dag:
    # Crea la tabla UsersInformation
    with open("./scripts/create.sql") as f:
        create_table = SQLExecuteQueryOperator(
            task_id="crate_table",
            conn_id="redshift_default",
            sql=f.read(),
            dag=dag,
        )

    # Elimina cargas previas del mismo dia
    with open("./scripts/clean_load_date.sql") as f:
        clean_load_date = SQLExecuteQueryOperator(
            task_id="clean_load_date",
            conn_id="redshift_default",
            sql=f.read(),
            dag=dag,
            parameters={"process_date": "{{ dag_run.conf }}"},
        )

    # Extrae la data de la API y la inserta en la tabla
    spark_etl_users = SparkSubmitOperator(
        task_id="spark_etl_users",
        application=f'{Variable.get("SPARK_SCRIPTS_DIR")}/ETL_usersinformation.py',
        conn_id="spark_default",
        dag=dag,
        driver_class_path=Variable.get("DRIVER_CLASS_PATH"),
        env_vars={"process_date": "{{ dag_run.conf }}"},
    )

    # Transforma la tabla UsersInformation
    with open("./scripts/update.sql") as d:
        update_table = SQLExecuteQueryOperator(
            task_id="update_table",
            conn_id="redshift_default",
            sql=d.read(),
            dag=dag,
        )

    create_table >> clean_load_date >> spark_etl_users >> update_table
