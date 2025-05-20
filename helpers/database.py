import json
import sqlite3
import os
class DataBase:
    def __init__(self):
        config_path = os.path.abspath("config.json")
        with open(config_path, "r") as file:
            js = json.load(file)
            print(js['path_to_database'])
            self.path_to_db = js['path_to_database']
        if(os.path.exists(self.path_to_db) == False):
            self.create_initial_db()
            
    def ___init__(self, path_to_db):
        self.path_to_db = path_to_db

    def create_initial_db(self):
        queries = {
            "experiments": '''
                CREATE TABLE IF NOT EXISTS "experiments" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "name" TEXT NOT NULL UNIQUE,
                    "folder_path" TEXT NOT NULL,
                    "created_at" DATE NOT NULL,
                    "edited_at" DATE NOT NULL,
                    "comment" TEXT NOT NULL
                );
            ''',

            "experiments_history": '''
                CREATE TABLE IF NOT EXISTS "experiments_history" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "experiment_id" INTEGER NOT NULL,
                    "experiment_version" INTEGER NOT NULL UNIQUE,
                    FOREIGN KEY("experiment_id") REFERENCES "experiments"("id") ON DELETE CASCADE
                );
            ''',

            "metrics": '''
                CREATE TABLE IF NOT EXISTS "metrics" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "name" TEXT NOT NULL UNIQUE
                );
            ''',

            "experiment_metrics": '''
                CREATE TABLE IF NOT EXISTS "experiment_metrics" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "metric_id" INTEGER NOT NULL,
                    "metric_value" REAL NOT NULL,
                    "experiment_history_id" INTEGER NOT NULL,
                    FOREIGN KEY("metric_id") REFERENCES "metrics"("id") ON DELETE CASCADE,
                    FOREIGN KEY("experiment_history_id") REFERENCES "experiments_history"("id") ON DELETE CASCADE
                );
            ''',

            "params": '''
                CREATE TABLE IF NOT EXISTS "params" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "name" TEXT NOT NULL UNIQUE
                );
            ''',

            "experiment_params": '''
                CREATE TABLE IF NOT EXISTS "experiment_params" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "param_id" INTEGER NOT NULL,
                    "param_value" TEXT NOT NULL,
                    "experiment_history_id" INTEGER NOT NULL,
                    FOREIGN KEY("param_id") REFERENCES "params"("id") ON DELETE CASCADE,
                    FOREIGN KEY("experiment_history_id") REFERENCES "experiments_history"("id") ON DELETE CASCADE
                );
            ''',

            "datasets": '''
                CREATE TABLE IF NOT EXISTS "datasets" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "name" TEXT NOT NULL UNIQUE,
                    "path_to_data" TEXT NOT NULL,
                    "description" TEXT,
                    "data_type" TEXT,
                    "created_at" DATE NOT NULL
                );
            ''',

            "experiment_data": '''
                CREATE TABLE IF NOT EXISTS "experiment_data" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "experiment_version_id" INTEGER NOT NULL UNIQUE,
                    "dataset_id" INTEGER NOT NULL,
                    FOREIGN KEY("experiment_version_id") REFERENCES "experiments_history"("id") ON DELETE CASCADE,
                    FOREIGN KEY("dataset_id") REFERENCES "datasets"("id") ON DELETE CASCADE
                );
            '''
        }

        import sqlite3
        conn = sqlite3.connect(self.path_to_db)
        cursor = conn.cursor()
        for table, query in queries.items():
            cursor.execute(query)
        conn.commit()
        conn.close()


    def run_query_params(self, query, params):
        conn = sqlite3.connect(self.path_to_db)
        conn.execute('PRAGMA foreign_keys = ON')
        cursor = conn.cursor()
        cursor.execute(query, params)
        
                
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        
        return results

    def run_query(self, query):
        conn = sqlite3.connect(self.path_to_db)
        conn.execute('PRAGMA foreign_keys = ON')
        cursor = conn.cursor()
        cursor.execute(query)
        
                
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        
        return results
    
    def select_from_table(self, table_name):
        conn = sqlite3.connect(self.path_to_db)
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name}')

            
        results = cursor.fetchall()
        conn.commit()
        conn.close()

        return results

        
    def export_db(self):
        pass
    
    def import_db(self):
        pass