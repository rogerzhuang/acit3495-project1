from flask import Flask, request, jsonify

app = Flask(__name__)

# This is a mock user database. In a real-world scenario, you'd use a proper database.
users = {
    "user1": "password1",
    "user2": "password2"
}

@app.route('/validate', methods=['POST'])
def validate():
    data = request.json
    userid = data.get('userid')
    password = data.get('password')
    
    if userid in users and users[userid] == password:
        return jsonify({"message": "Authentication successful", "userid": userid}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)