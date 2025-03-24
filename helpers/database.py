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
                CREATE TABLE "experiments" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "name" TEXT NOT NULL UNIQUE,
                    "folder_path" TEXT NOT NULL,
                    "created_at" DATE NOT NULL,
                    "edited_at" DATE NOT NULL,
                    "comment" TEXT NOT NULL
                );
            ''',
            "models": '''
                CREATE TABLE "models" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "name" VARCHAR(255) NOT NULL
                );
            ''',
            "experiments_history": '''
                CREATE TABLE "experiments_history" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "experiment_id" INTEGER NOT NULL,
                    "experiment_version" INTEGER NOT NULL UNIQUE,
                    FOREIGN KEY("experiment_id") REFERENCES "experiments"("id") ON DELETE CASCADE
                );
            ''',
            "experiment_results": '''
                CREATE TABLE "experiment_results" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "experiment_history_id" INTEGER NOT NULL,
                    "metric_id" INTEGER NOT NULL,
                    "metric_result" FLOAT NOT NULL,
                    "created_at" DATE NOT NULL,
                    FOREIGN KEY("experiment_history_id") REFERENCES "experiments_history"("id"),
                    FOREIGN KEY("metric_id") REFERENCES "metrics"("id")
                );
            ''',
            "metrics": '''
                CREATE TABLE "metrics" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "name_full" VARCHAR(255) NOT NULL,
                    "name_short" VARCHAR(255) NOT NULL,
                    "description" TEXT NOT NULL
                );
            ''',
            "experiment_models": '''
                CREATE TABLE "experiment_models" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "experiment_history_id" INTEGER NOT NULL,
                    "model_id" INTEGER NOT NULL,
                    FOREIGN KEY("experiment_history_id") REFERENCES "experiments_history"("id") ON DELETE CASCADE,
                    FOREIGN KEY("model_id") REFERENCES "models"("id") ON DELETE CASCADE

                );
            ''',
            "model_hyperparameters": '''
                CREATE TABLE "model_hyperparameters" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "experiment_models_id" INTEGER NOT NULL,
                    "params" TEXT NOT NULL,
                    FOREIGN KEY("experiment_models_id") REFERENCES "experiment_models"("id")
                    ON DELETE CASCADE
                );
            ''',
            "experiment_data": '''
                CREATE TABLE "experiment_data" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "experiment_version_id" INTEGER NOT NULL,
                    "path_to_data" VARCHAR(255),
                    FOREIGN KEY("experiment_version_id") REFERENCES "experiments_history"("id")
                    ON DELETE CASCADE
                );
            '''
        }

        for key, values in queries.items():
            conn = sqlite3.connect(self.path_to_db)

            conn.execute(values)

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