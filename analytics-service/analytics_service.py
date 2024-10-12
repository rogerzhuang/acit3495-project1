import time
import mysql.connector
import os
from pymongo import MongoClient
from mysql.connector import Error
import numpy as np
from scipy.stats import zscore  # For outlier detection using Z-score

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
    z_scores = zscore(values)
    outliers = np.where(np.abs(z_scores) > 3)  # Outliers defined as data points where Z > 3
    return outliers[0].tolist()

def calculate_analytics():
    mysql_conn = get_mysql_connection()
    cursor = mysql_conn.cursor()
    
    cursor.execute("SELECT userid, value, timestamp FROM data")
    results = cursor.fetchall()
    
    analytics = {}
    for userid, value, timestamp in results:
        if userid not in analytics:
            analytics[userid] = {"values": [], "timestamps": []}
        analytics[userid]["values"].append(value)
        analytics[userid]["timestamps"].append(timestamp)
    
    for userid, data in analytics.items():
        values = np.array(data["values"])
        timestamps = np.array(data["timestamps"])
        
        # Calculate trend analysis
        rate_of_change = np.diff(values) / values[:-1]  # Calculate the rate of change
        rolling_avg = np.convolve(values, np.ones(5)/5, mode='valid')  # 5-point rolling average
        
        analytics[userid] = {
            "max": np.max(values),
            "min": np.min(values),
            "avg": np.mean(values),
            "count": len(values),
            "std_dev": np.std(values),
            "median": np.median(values),
            "sum": np.sum(values),
            "range": np.ptp(values),
            "variance": np.var(values),
            "percentiles": np.percentile(values, [25, 50, 75]),
            "iqr": np.percentile(values, 75) - np.percentile(values, 25),
            "outliers": detect_outliers(values),  # List of outliers
            "rate_of_change": rate_of_change.tolist(),  # Track how values change over time
            "rolling_avg": rolling_avg.tolist(),  # Rolling average for trend analysis
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
