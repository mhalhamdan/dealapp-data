import logging
import sqlite3
from schema import LISTING_TABLE_SCHEMA, CITY_TABLE_SCHEMA, CATEGORY_TABLE_SCHEMA, PROPERTY_TABLE_SCHEMA

class SqliteClient:

    def __init__(self) -> None:
        self.con = sqlite3.connect("deals_data.db")
        self.cur = self.con.cursor()

        self.create_table("city", ", ".join(CITY_TABLE_SCHEMA))
        self.create_table("category", ", ".join(CATEGORY_TABLE_SCHEMA))
        self.create_table("propertyType", ", ".join(PROPERTY_TABLE_SCHEMA))
        self.create_table("listing", ", ".join(LISTING_TABLE_SCHEMA))

        self.cur.execute("CREATE INDEX if not exists idx_category_id ON listing(categoryId)")
        self.cur.execute("CREATE INDEX if not exists idx_city_id ON listing(cityId)")
        self.con.commit()

    def create_table(self, table_name: str, columns: list):
        """Creates a table if it does not exist.

        Args:
            table_name (str): name of the table to be created.
            columns (list[str]): the columns of the table to be created.
        """
        self.cur.execute(f"CREATE TABLE if not exists {table_name} ({columns})")
        self.con.commit()


    def delete_record(self, table_name: str, record_id: str):
        """Deletes a record from a table.

        Args:
            table_name (str): name of the table.
            record_id (str): id of the record to be deleted.
        """
        self.cur.execute(f"DELETE FROM {table_name} WHERE {table_name}Id = ?", (record_id,))
        self.con.commit()

    def insert_lookup_table(self, table_name: str):
        """Inserts data into a lookup table.

        Args:
            table_name (str): name of the table.
        """
        columns = f"{table_name}Id, {table_name}NameEn, {table_name}NameAr"
        self.cur.execute(f"""
                        INSERT OR IGNORE INTO {table_name} ({columns}) 
                        SELECT DISTINCT {columns} 
                        FROM listing"""
        )
        self.con.commit()

        # Get number of rows changed
        logging.info(f"Added {self.cur.rowcount} new rows to {table_name} table.")