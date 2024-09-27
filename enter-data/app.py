from flask import Flask, request, jsonify
import mysql.connector
import requests

app = Flask(__name__)

@app.route('/enter-data', methods=['POST'])
def enter_data():
    data = request.json
    userid = data.get('userid')
    password = data.get('password')
    value = data.get('value')

    if not all([userid, password, value]):
        return jsonify({"error": "Missing required fields"}), 400

    auth_response = requests.post('http://authentication-service:8000/validate', 
                                  json={'userid': userid, 'password': password})
    
    if auth_response.status_code != 200:
        return jsonify({"error": "Invalid credentials"}), 401

    conn = mysql.connector.connect(
        host="mysql",
        user="root",
        password="rootpassword",
        database="datadb"
    )
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO data (userid, value) VALUES (%s, %s)", (userid, value))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return jsonify({"message": "Data entered successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)