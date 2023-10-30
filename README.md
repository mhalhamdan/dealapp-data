# dealapp-data
For quant assessment.

## Introduction
I tried to approach this assessment initially with a minimal approach, using only the built-in sqlite3 python library, so that anyone cloning the repo can easily reproduce the results. However, after learning a bit more about Airflow as a framework I realized that it works best connecting with remote databases, since it is intended to be an orchestrator first and foremost. 

Saying that, I believe my solution still does not use Airflow in the best way possible. Because it still performs a lot of computations in PythonOperator (to collect and transform the data). A better solution would move this logic to a different location and have Airflow trigger the workflow responsible for dealing with the data directly.

## Discovery
First I explored the website [https://dealapp.sa/](https://dealapp.sa/), turned on inspect element and checked the Network tab to see what calls were being made in the main page. I soon found the main [API "https://api.dealapp.sa/production/ad"]("https://api.dealapp.sa/production/ad") which was using a bearer token for authorization. And to my luck it seems that the token does not expire. 

I then looked at the data format using Postman to call the API and try our parameters like limit and page. I found headers like ```X-RateLimit-Remaining``` which were relevant since we want to rate limit our calls so that we don't overwhelm the API or get flagged. I also ran a Python script `analysis.py` to check how many columns exist in the data.

## Folder structure
```
dags
└── deals_data
    ├── modules
    │   ├── __init__.py
    │   ├── collect_data.py
    │   ├── config.py
    │   ├── config.yaml 
    │   ├── helper.py
    │   ├── insert.py
    │   └── schema.py
    ├── pipeline.py
    └── requirements.txt
```
pipeline.py is where the DAG is defined, and modules houses python code to help collect and transform the data.
Took inspiration from [https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html]([https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html])

## Teck stack
For this assessment, I have used the following tech stack:
- Airflow: for scheduling and orchestrating.
- Postgres: Database hosted on Azure to store the listings.
- Requests & Pandas (Python): To retrieve results from the API and manipulate the data.

## Architecture
[ Add illustration here]
NOTICE: I did not change the default Sqlite metadata DB for Airflow. In a production environment it would make sense to switch it out because Sqlite is intended for development only as highlighted in: [https://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html)

## Security

For the purposes of this assessment, in the firewall rules I have enabled public access so that the team can review the database. In a production environment I would restrict the access to a few IP addresses. I also enabled SQL login with credentials, but a better way of managing DB access would be through an identity provider which Azure provides, so that we can manage the roles and access of persons in regards to sensitive data.

For secrets management, I would use Azure Key Vault and inject them at deployment in a production environment. 

### SQL Injection
Used pandas to_sql() [https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html) to insert rows into a temporary table for ease of formatting and to prevent sql injection (I have tested this). 

## Schedule 
Airflow is scheduled to run the DAG with the following configuration
```python
with DAG (
    'deals_data_pipeline', 
    start_date=datetime(2023, 1, 1), 
    schedule='@daily',
    catchup=False
) as dag:
```
which means it will run 12:00 AM == 00:00 UTC daily.

## Challenges

- If you are using MacOS, you might need to set an environment variable ```export NO_PROXY="*"``` for the requests library to work inside Airflow. For a while the pipeline would freeze and crash with no useful logs until I found a discussion where they discussed the same issue on a MacOS environment.

- I rarely ever write raw SQL queries, I usually use an ORM to manage that for me. But for this assessment I really wanted to try the SQLExecuteQueryOperator which takes in sql statements. I still think it is better to use ORMs for better consistency and less time worrying about single and double quotes everywhere.
  
- After my initial solution with Sqlite, I tried using Microsoft SQL Server and writing raw sql queries. It was a very unpleasant experience dealing with TRANSACT-SQL for the first and last time hopefully. Switched to Postgres in the end because I was more familiar with it.

