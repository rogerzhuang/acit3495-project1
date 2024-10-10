import time
import mysql.connector
import os
from pymongo import MongoClient
from mysql.connector import Error


def get_mysql_connection(max_retries=5, delay=5):
    for attempt in range(max_retries):
        host = os.environ['READ_DB_HOST']
        user = os.environ['READ_DB_USER']
        password = os.environ['READ_DB_PASSWORD']
        database = os.environ['READ_DB_NAME']
        print(f"db host: {host}")
        print(f"db user: {user}")
        print(f"db password: {password}")
        print(f"db database: {database}")
        try:
            return mysql.connector.connect(
                host=os.environ['READ_DB_HOST'],
                user=os.environ['READ_DB_USER'],
                password=os.environ['READ_DB_PASSWORD'],
                database=os.environ['READ_DB_NAME']
            )
        except Error as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise e


def get_mongodb_connection():
    # Connection details
    mongo_host = os.environ['WRITE_DB_HOST']  # or the IP/hostname of your MongoDB server
    database_name = os.environ['WRITE_DB_NAME']  # or the name of your database
    username = os.environ['WRITE_DB_USER']  # or the username of your database
    password = os.environ['WRITE_DB_PASSWORD']  # or the password of your database
    uri = f"mongodb://{username}:{password}@{mongo_host}/{database_name}"
    return MongoClient(uri)


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
        time.sleep(60)  # Run every minute