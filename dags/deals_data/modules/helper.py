"""helper.py
Contains helper functions for the DAGs.
"""

def format_schema(schema: list) -> list: # For the pesky double quotes
    formatted_schema = [f"\"{x.split(' ')[0]}\"{x[len(x.split(' ')[0]):]}" for x in schema]
    return formatted_schema


def get_create_table_sql_statement(table_name: str, schema: list) -> str:
    return f"""CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(schema)});"""


def construct_sql_update_statement(columns: list) -> str:
    rows = []
    for column in columns:
        rows.append(f"\"{column}\" = EXCLUDED.\"{column}\"")
    return f"SET {', '.join(rows)}"

def construct_insert_lookup_table_statement(table_name: str):
    columns = f"\"{table_name}Id\", \"{table_name}NameEn\", \"{table_name}NameAr\""
    statement = f"""
        INSERT INTO {table_name} ({columns}) 
        SELECT DISTINCT {columns} 
        FROM listingtemptable
        ON CONFLICT (\"{table_name}Id\") 
        DO NOTHING;"""
    return statement