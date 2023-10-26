import time
import logging
from collections import defaultdict
import requests
import pandas as pd
from credentials import TOKEN
from schema import CITY_COLUMNS, LISTING_COLUMNS, CATEGORY_COLUMNS, PROPERTY_COLUMNS, ALL_RAW_COLUMNS_TO_PARSE
from sqlite_connector import SqliteClient

logging.getLogger().setLevel(logging.INFO)

API_URL = "https://api.dealapp.sa/production/ad"

sqlite_client = SqliteClient()


def get_data(limit=1, page=1) -> requests.Response:
    response = requests.get(
        API_URL, 
        headers={"Authorization": TOKEN},
        params={
            "limit": limit,
            "page": page
        }
    )
    return response


def get_data_rate_limited():
    LIMIT = 10
    SLEEP_TIME = 60

    # Determine how many pages to get
    has_next_page = True
    page = 1
    data = []

    # Get data from each page
    while has_next_page:

        response = get_data(limit=LIMIT, page=page)
        has_next_page = response.json()["hasNextPage"]
        total_pages = response.json()["totalPage"]
        calls_left = int(response.headers["X-RateLimit-Remaining"])
        # date = response.headers["Date"]
        # timestamp = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z").timestamp()
        # timestamp_reset = float(response.headers["X-RateLimit-Reset"])
        # Time until reset
        # logging.info(f"Time until reset: {timestamp_reset - timestamp} seconds")
        total = response.json()["total"]

        logging.info(f"Retrieving page {page} of {total_pages} pages. Calls left: {calls_left}")

        data += response.json()["data"]

        if calls_left <= 1:
            logging.info(f"Ran out of calls, sleeping for {SLEEP_TIME} seconds...")
            time.sleep(SLEEP_TIME)

        time.sleep(1)

        if page > 5:
            break

        page += 1

    return data, total

def parse_response_to_df(response: dict) -> pd.DataFrame:

    parsed_data = defaultdict(list) # We use defaultdict so we can append without initializing the keys first.

    for data in response:
        for column in ALL_RAW_COLUMNS_TO_PARSE:
            if column in data.keys():
                parsed_data[column].append(data[column])
            else:
                parsed_data[column].append(None)
            
    df = pd.DataFrame(parsed_data)

    df.rename(columns={"_id": "listingId"}, inplace=True)

    # Parse propertyType
    df["propertyTypeId"] = df["propertyType"].apply(lambda x: x["_id"] if x else None)
    df["propertyTypeNameEn"] = df["propertyType"].apply(lambda x: x["propertyType"] if x else None)
    df["propertyTypeNameAr"] = df["propertyType"].apply(lambda x: x["propertyType_ar"] if x else None)

    # Parse category
    df["categoryId"] = df["propertyType"].apply(lambda x: x["category"]["_id"] if x else None)
    df["categoryNameEn"] = df["propertyType"].apply(lambda x: x["category"]["name_en"] if x else None)
    df["categoryNameAr"] = df["propertyType"].apply(lambda x: x["category"]["name_ar"] if x else None)

    # Parse city
    df["cityId"] = df["city"].apply(lambda x: x["_id"] if x else None)
    df["cityNameEn"] = df["city"].apply(lambda x: x["name_en"] if x else None)
    df["cityNameAr"] = df["city"].apply(lambda x: x["name_ar"] if x else None)

    # Parse district
    df["districtId"] = df["district"].apply(lambda x: x["_id"] if x else None)
    df["districtNameEn"] = df["district"].apply(lambda x: x["name_en"] if x else None)
    df["districtNameAr"] = df["district"].apply(lambda x: x["name_ar"] if x else None)

    # Parse refreshed
    df["refreshedAt"] = df["refreshed"].apply(lambda x: x["at"] if x else None)

    # If a column is a dictionary convert it to a string
    for column in df.columns:
        if df[column].dtype == "object":
            df[column] = df[column].apply(lambda x: str(x))

    return df


def remove_rows_that_exist_in_db(data: pd.DataFrame, table_name: str) -> pd.DataFrame:
    # Get the ids that exist in the database
    id_name = f"{table_name}Id"
    existing_ids = pd.read_sql(f"SELECT {id_name} FROM {table_name}", sqlite_client.con)

    # Remove the rows that exist in the database
    data = data[~data[id_name].isin(existing_ids[id_name])]
    return data


def delete_listings_that_refreshed(new_listings: pd.DataFrame) -> None:
    existing_listings = pd.read_sql(f"SELECT listingId, refreshedAt FROM listing", sqlite_client.con)

    # Get all instances where data.refreshedAt != existing_listings.refreshedAt
    refreshed_listings = pd.merge(new_listings, existing_listings, on="listingId", how="inner", suffixes=("_a", "_b"))
    refreshed_listings = refreshed_listings[refreshed_listings["refreshedAt_a"] != refreshed_listings["refreshedAt_b"]]

    # Iterate listing ids
    for listing_id in refreshed_listings["listingId"].values:
        sqlite_client.delete_record("listing", listing_id)
        logging.info(f"Deleted listing {listing_id} because it was refreshed and will be updated.")



def df_to_sql_table(data: pd.DataFrame, table_name: str, columns: list) -> None:
    df = data[columns]

    # Get unique rows
    df = df.drop_duplicates()

    # Delete refreshed rows
    if table_name == "listing":
        delete_listings_that_refreshed(df[["listingId", "refreshedAt"]])

    df = remove_rows_that_exist_in_db(df, table_name)
    if df.shape[0] == 0:
        logging.info(f"No new data to add to the database for {table_name} table.")
        return

    df.to_sql(table_name, sqlite_client.con, if_exists="append", index=False)
    logging.info(f"Added {df.shape[0]} rows to {table_name} table.")


def main():
    data, _ = get_data_rate_limited()
    data_df = parse_response_to_df(data)

    df_to_sql_table(data_df.copy(), "city", CITY_COLUMNS)

    df_to_sql_table(data_df.copy(), "category", CATEGORY_COLUMNS)

    df_to_sql_table(data_df.copy(), "propertyType", PROPERTY_COLUMNS)

    df_to_sql_table(data_df.copy(), "listing", LISTING_COLUMNS)


if __name__ == "__main__":
    main()