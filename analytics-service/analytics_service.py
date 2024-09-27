import time
import mysql.connector
from pymongo import MongoClient
from mysql.connector import Error

def get_mysql_connection(max_retries=5, delay=5):
    for attempt in range(max_retries):
        try:
            return mysql.connector.connect(
                host="mysql",
                user="root",
                password="rootpassword",
                database="datadb"
            )
        except Error as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise e

def get_mongodb_connection():
    return MongoClient('mongodb://mongodb:27017')

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
        values = data["values"]
        analytics[userid] = {
            "max": max(values),
            "min": min(values),
            "avg": sum(values) / len(values),
            "count": len(values)
        }
    
    cursor.close()
    mysql_conn.close()
    
    mongo_client = get_mongodb_connection()
    db = mongo_client.analyticsdb
    collection = db.analytics
    
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
        time.sleep(60)  # Run every minute