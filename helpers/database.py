import json
import psycopg2
import pandas as pd
from psycopg2.extras import RealDictCursor

class DataBase:
    def __init__(self):
        config_path = "config.json"
        with open(config_path, "r") as file:
            config = json.load(file)
        self.conn_params = {
            "host": config["host"],
            "port": config["port"],
            "dbname": config["database"],
            "user": config["user"],
            "password": config["password"],
            "cursor_factory": RealDictCursor
            
        }
        self.conn = None

    def connect(self):
        if self.conn is None or self.conn.closed != 0:
            self.conn = psycopg2.connect(**self.conn_params)

    def close(self):
        if self.conn and self.conn.closed == 0:
            self.conn.close()

    def run_query_with_column_names(self, query):
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
        self.close()
        return pd.DataFrame(data, columns=column_names)

    def run_query_params(self, query, params):
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            
            if query.strip().lower().startswith("select"):
                results = cursor.fetchall()
            else:
                results = None  # Або [] — залежно від логіки
            
            self.conn.commit()
        self.close()
        return results


    def run_query(self, query):
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            
            if query.strip().lower().startswith("select"):
                results = cursor.fetchall()
            else:
                results = None  
            
            self.conn.commit()
        self.close()
        return results

    def select_from_table(self, table_name):
        query = f"SELECT * FROM {table_name}"
        return self.run_query(query)
