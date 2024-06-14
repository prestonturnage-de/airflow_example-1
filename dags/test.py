import os
import json
import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

# Build an Airflow DAG
with DAG(
  dag_id="simple_operators", # The name that shows up in the UI
  start_date=pendulum.today(), # Start date of the DAG
  catchup=False,
) as dag:
  # create an operator that runs an ls command
  op1 = BashOperator(task_id='lstask', bash_command='ls')
  # create an operator that runs the date command
  op2 = BashOperator(task_id='datetask', bash_command='date')
  # run the date operator after the ls operator, dependent upon its success
  op1 >> op2

# if __name__ == "__main__":
#   dag.cli()