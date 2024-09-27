const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql2/promise');
const axios = require('axios');

const app = express();
const port = 8001;

app.use(bodyParser.json());

const dbConfig = {
    host: "mysql",
    user: "root",
    password: "rootpassword",
    database: "datadb"
};

app.post('/enter-data', async (req, res) => {
    const { userid, password, value } = req.body;

    if (!userid || !password || !value) {
        return res.status(400).json({ error: "Missing required fields" });
    }

    try {
        const authResponse = await axios.post('http://authentication-service:8000/validate', { userid, password });
        
        if (authResponse.status !== 200) {
            return res.status(401).json({ error: "Invalid credentials" });
        }

        const connection = await mysql.createConnection(dbConfig);
        
        await connection.execute('INSERT INTO data (userid, value) VALUES (?, ?)', [userid, value]);
        
        await connection.end();
        
        res.status(200).json({ message: "Data entered successfully" });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: "An error occurred" });
    }
});

app.listen(port, () => {
    console.log(`Enter-data service listening at http://localhost:${port}`);
});
