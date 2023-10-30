import json
from collections import defaultdict
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from deals_data.modules.config import config
from deals_data.modules.schema import ALL_RAW_COLUMNS_TO_PARSE, LISTING_COLUMNS

def parse_response_to_df(response: dict) -> pd.DataFrame:

    parsed_data = defaultdict(list) # We use defaultdict so we can append without initializing the keys first.

    for data in response:
        for column in ALL_RAW_COLUMNS_TO_PARSE:
            if column in data.keys():
                parsed_data[column].append(data[column])
            else:
                parsed_data[column].append(None)
            
    df = pd.DataFrame(parsed_data)

    # rename read to readFlag (because of a microsoft sql issue with the column name)
    df.rename(columns={"_id": "listingId", "read": "readFlag"}, inplace=True)

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

    # Iterate and handle types
    for column in df.columns:
        if df[column].dtype == "object":
            # If dictionary, parse to json string, else replace single quotes with double-single quotes
            if df[column].apply(lambda x: isinstance(x, dict) or isinstance(x, list)).any():
                df[column] = df[column].apply(lambda x: json.dumps(x))
            else:
                df[column] = df[column].apply(lambda x: x.replace("'", "") if x else "None")
        if df[column].dtype == "bool":
            df[column] = df[column].apply(lambda x: str(x))

    df = df.drop_duplicates(["listingId"])
    df = df[LISTING_COLUMNS]

    return df


def push_data_to_postgres(df: pd.DataFrame, table_name: str) -> None:

    conn_uri = URL.create(
        drivername="postgresql",
        username=config["SQL_USERNAME"],
        password=config["SQL_PASSWORD"],
        host=config["SQL_HOST"],
        port=5432,
        database=config["SQL_DB"]
    )
    engine = create_engine(conn_uri)
    Session = sessionmaker(bind=engine)
    session = Session()

    df.to_sql(table_name, con=session.get_bind(), if_exists='append', index=False)

def parse_and_push(response: dict, table_name="listingtemptable") -> None:

    df = parse_response_to_df(response)

    push_data_to_postgres(df, table_name)



