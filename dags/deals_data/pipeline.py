import logging
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from deals_data.modules.collect_data import get_data_rate_limited
from deals_data.modules.insert import parse_and_push
from deals_data.modules.helper import get_create_table_sql_statement, construct_sql_update_statement, construct_insert_lookup_table_statement, format_schema
from deals_data.modules.schema import *


with DAG (
    'deals_data_pipeline', 
    start_date=datetime(2023, 1, 1), 
    schedule='@daily',
    catchup=False
) as dag:

    conn_id = "postgres-deals"

    task1 = SQLExecuteQueryOperator(
        task_id="create_lookup_tables",
        conn_id=conn_id,
        autocommit=True,
        sql=f"""
            {get_create_table_sql_statement("city", format_schema(CITY_TABLE_SCHEMA))}
            {get_create_table_sql_statement("category", format_schema(CATEGORY_TABLE_SCHEMA))}
            {get_create_table_sql_statement("propertyType", format_schema(PROPERTY_TABLE_SCHEMA))}"""
    )

    task2 = SQLExecuteQueryOperator(
        task_id="create_listing_table_and_index",
        conn_id=conn_id,
        autocommit=True,
        sql= f"""
            DROP TABLE IF EXISTS listingtemptable;
            {get_create_table_sql_statement("listingtemptable", format_schema(LISTING_TABLE_SCHEMA))}
            {get_create_table_sql_statement("listing", format_schema(LISTING_TABLE_SCHEMA) + FOREIGN_KEY_CONSTRAINTS)}
            CREATE INDEX IF NOT EXISTS idx_cityId ON listing (\"cityId\");
            CREATE INDEX IF NOT EXISTS idx_categoryId ON listing (\"categoryId\");
            CREATE INDEX IF NOT EXISTS idx_propertyTypeId ON listing (\"propertyTypeId\");
        """
    )

    task3 = PythonOperator(task_id='collect_data', python_callable=get_data_rate_limited)

    task4 = PythonOperator(task_id='parse_and_push', python_callable=parse_and_push, op_kwargs={'response': task3.output})

    task5 = SQLExecuteQueryOperator(
        task_id="populate_lookup_tables",
        conn_id=conn_id,
        autocommit=True,
        sql=f"""
            -- Populate lookup tables (city, category, propertyType)
            {construct_insert_lookup_table_statement("city")}

            {construct_insert_lookup_table_statement("category")}

            {construct_insert_lookup_table_statement("propertyType")}
        """
    )

    task6 = SQLExecuteQueryOperator(
        task_id="populate_listing_table",
        conn_id=conn_id,
        autocommit=True,
        sql=f"""
            INSERT INTO listing ({', '.join(format_schema(LISTING_COLUMNS))})
            SELECT * FROM listingtemptable
            ON CONFLICT (\"listingId\") 
            DO UPDATE
            {construct_sql_update_statement(LISTING_COLUMNS)}
            WHERE listing.\"refreshedAt\" <> EXCLUDED.\"refreshedAt\";
        """
    )

    task1 >> task2 >> task3 >> task4 >> task5 >> task6
