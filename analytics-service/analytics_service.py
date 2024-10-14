import os
import time
import mysql.connector
from pymongo import MongoClient

def get_mysql_connection():
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'mysql'),
        user=os.environ.get('MYSQL_USER', 'reader'),
        password=os.environ.get('MYSQL_PASSWORD', 'readerpassword'),
        database=os.environ.get('MYSQL_DATABASE', 'datadb')
    )

def get_mongodb_connection():
    return MongoClient(os.environ.get('MONGO_URI', 'mongodb://writer:writerpassword@mongodb:27017/analyticsdb'))

def calculate_analytics():
    mysql_conn = get_mysql_connection()
    cursor = mysql_conn.cursor()
    
    # Simplified query, just getting all values for each user
    cursor.execute("SELECT userid, value FROM data")
    results = cursor.fetchall()
    
    # Simplified analytics logic (just calculating sum and count)
    analytics = {}
    for userid, value in results:
        if userid not in analytics:
            analytics[userid] = {"sum": 0, "count": 0}
        analytics[userid]["sum"] += value
        analytics[userid]["count"] += 1
    
    cursor.close()
    mysql_conn.close()
    
    # Store results in MongoDB
    mongo_client = get_mongodb_connection()
    db = mongo_client.analyticsdb
    collection = db.analytics
    
    # Store sum and count for each user
    for userid, data in analytics.items():
        collection.update_one(
            {"userid": userid},
            {"$set": {"sum": data["sum"], "count": data["count"]}},
            upsert=True
        )
    
    mongo_client.close()

if __name__ == "__main__":
    while True:
        try:
            calculate_analytics()
            print("Analytics calculated and stored successfully")
        except Exception as e:
            print(f"An error occurred: {e}")
        time.sleep(60)  # Run every minute
