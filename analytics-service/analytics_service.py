import time
import mysql.connector
import os
from pymongo import MongoClient
from mysql.connector import Error
import numpy as np

def get_mysql_connection(max_retries=5, delay=5):
    for attempt in range(max_retries):
        host = os.environ['READ_DB_HOST']
        user = os.environ['READ_DB_USER']
        password = os.environ['READ_DB_PASSWORD']
        database = os.environ['READ_DB_NAME']
        try:
            return mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
        except Error as e:
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                raise e

def get_mongodb_connection():
    mongo_host = os.environ['WRITE_DB_HOST']
    database_name = os.environ['WRITE_DB_NAME']
    username = os.environ['WRITE_DB_USER']
    password = os.environ['WRITE_DB_PASSWORD']
    uri = f"mongodb://{username}:{password}@{mongo_host}/{database_name}"
    return MongoClient(uri)

def detect_outliers(values):
    threshold = 3
    mean = np.mean(values)
    std_dev = np.std(values)
    outliers = [x for x in values if abs(x - mean) > threshold * std_dev]
    return outliers

def normalize_data(values):
    min_val = np.min(values)
    max_val = np.max(values)
    if max_val - min_val == 0:
        return values  # Return as is if all values are the same
    normalized = (values - min_val) / (max_val - min_val)
    return normalized

def categorize_values(values):
    categories = []
    for value in values:
        if value < 25:
            categories.append('low')
        elif 25 <= value < 75:
            categories.append('medium')
        else:
            categories.append('high')
    return categories

def calculate_percentiles(values):
    percentiles = {
        "25th_percentile": np.percentile(values, 25),
        "50th_percentile": np.percentile(values, 50),
        "75th_percentile": np.percentile(values, 75)
    }
    return percentiles

def calculate_analytics():
    mysql_conn = get_mysql_connection()
    cursor = mysql_conn.cursor()
    
    cursor.execute("SELECT userid, value FROM data")
    results = cursor.fetchall()
    
    analytics = {}
    for userid, value in results:
        if userid not in analytics:
            analytics[userid] = {"values": []}
        analytics[userid]["values"].append(value)
    
    for userid, data in analytics.items():
        values = np.array(data["values"])
        
        analytics[userid] = {
            "max": np.max(values),
            "min": np.min(values),
            "avg": np.mean(values),
            "count": len(values),
            "std_dev": np.std(values),
            "sum": np.sum(values),
            "outliers": detect_outliers(values),  # Simple outlier detection
            "normalized_values": normalize_data(values).tolist(),  # Normalize values between 0 and 1
            "categories": categorize_values(values),  # Categorize values as 'low', 'medium', 'high'
            "percentiles": calculate_percentiles(values),  # Calculate 25th, 50th, and 75th percentiles
        }
    
    cursor.close()
    mysql_conn.close()
    
    mongo_client = get_mongodb_connection()
    db = mongo_client[os.environ['WRITE_DB_NAME']]
    collection = db[os.environ['WRITE_DB_COLLECTION']]
    
    for userid, data in analytics.items():
        collection.update_one(
            {"userid": userid},
            {"$set": data},
            upsert=True
        )
    
    mongo_client.close()

if __name__ == '__main__':
    while True:
        calculate_analytics()
        time.sleep(60)
