import logging
from collections import defaultdict
import requests
import pandas as pd
from credentials import TOKEN
from schema import CITY_COLUMNS, LISTING_COLUMNS, CATEGORY_COLUMNS, PROPERTY_COLUMNS, COLUMNS_THAT_EXPAND, COLUMNS_TO_IGNORE
from sqlite_connector import SqliteClient

logging.getLogger().setLevel(logging.INFO)

API_URL = "https://api.dealapp.sa/production/ad"

sqlite_client = SqliteClient()

def get_data():
    response = requests.get(
        API_URL, 
        headers={"Authorization": TOKEN},
        params={
            "limit": 2,
            "page": 10
        }
    )
    return response.json()

def parse_response_to_df(response: dict) -> pd.DataFrame:

    parsed_data = defaultdict(list) # We use defaultdict so we can append without initializing the keys first.

    for data in response["data"]:
        
        for column, value in data.items():

            if column == "_id":
                parsed_data["listingId"].append(value)

            if column in COLUMNS_TO_IGNORE:
                continue

            if column not in COLUMNS_THAT_EXPAND:
                parsed_data[column].append(value)
                
            elif column == "propertyType":
                parsed_data["propertyTypeId"].append(value["_id"])
                parsed_data["propertyTypeNameEn"].append(value["propertyType"])
                parsed_data["propertyTypeNameAr"].append(value["propertyType_ar"])

                parsed_data["categoryId"].append(value["category"]["_id"])
                parsed_data["categoryNameEn"].append(value["category"]["name_en"])
                parsed_data["categoryNameAr"].append(value["category"]["name_ar"])
        
            elif column == "city":
                parsed_data["cityId"].append(value["_id"])
                parsed_data["cityNameEn"].append(value["name_en"])
                parsed_data["cityNameAr"].append(value["name_ar"])

            elif column == "district":
                parsed_data["districtId"].append(value["_id"])
                parsed_data["districtNameEn"].append(value["name_en"])
                parsed_data["districtNameAr"].append(value["name_ar"])
            
            elif column == "relatedQuestions":
                parsed_data["relatedQuestions"].append(value)
            
            elif column == "refreshed":
                parsed_data["refreshedAt"].append(value["at"])

            else:
                # Serialize dict to string
                parsed_data[column].append(str(value))

    return pd.DataFrame(parsed_data)

def remove_rows_that_already_exist(data: pd.DataFrame, table_name: str) -> pd.DataFrame:
    # Get the ids that exist in the database
    id_name = f"{table_name}Id"
    existing_ids = pd.read_sql(f"SELECT {id_name} FROM {table_name}", sqlite_client.con)

    # Remove the rows that exist in the database
    data = data[~data[id_name].isin(existing_ids[id_name])]
    return data

def df_to_sql_table(data: pd.DataFrame, table_name: str, columns: list) -> None:
    df = data[columns]

    if table_name != "listing":
        # Get unique rows
        df = df.drop_duplicates()

    df = remove_rows_that_already_exist(df, table_name)
    if df.shape[0] == 0:
        logging.info(f"No new data to add to the database for {table_name} table.")
        return

    df.to_sql(table_name, sqlite_client.con, if_exists="append", index=False)
    logging.info(f"Added {df.shape[0]} rows to {table_name} table.")


def main():
    data = get_data()
    data_df = parse_response_to_df(data)

    df_to_sql_table(data_df.copy(), "city", CITY_COLUMNS)

    df_to_sql_table(data_df.copy(), "category", CATEGORY_COLUMNS)

    df_to_sql_table(data_df.copy(), "propertyType", PROPERTY_COLUMNS)

    df_to_sql_table(data_df.copy(), "listing", LISTING_COLUMNS)



    # print(data_df)

if __name__ == "__main__":
    main()