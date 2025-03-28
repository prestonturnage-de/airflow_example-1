# from airflow.decorators import dag
from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from random import randint

def _training_model():
    return randint(1, 10)

def _choose_best_model(ti):
    accuracies = ti.xcom_pull(task_ids = [
        "training_model_a",
        "training_model_b",
        "training_model_c"
    ])
    best_accuracy = max(accuracies)
    if (best_accuracy > 8):
        return 'accurate'
    else:
        return 'inaccurate'


with DAG(
    dag_id="my_dag", 
    start_date = datetime(2025, 1, 1), 
    schedule_interval = "@daily", 
    catchup = False
    ) as dag:
        training_model_A = PythonOperator(
            task_id = "training_model_a",
            python_callable = _training_model
        )
        training_model_B = PythonOperator(
            task_id = "training_model_b",
            python_callable = _training_model
        )
        training_model_C = PythonOperator(
            task_id = "training_model_c",
            python_callable = _training_model
        )

        choose_best_model = BranchPythonOperator(
            task_id = "_choose_best_model",
            python_callable = _choose_best_model
        )
        
        accurate = BashOperator(
            task_id = "accurate",
            bash_command = "echo 'accurate'"
        )

        inaccurate = BashOperator(
            task_id = "inaccurate",
            bash_command = "echo 'accurate'"
        )

        [training_model_A, training_model_B, training_model_C] >> choose_best_model >> [accurate, inaccurate]