const express = require('express');
const axios = require('axios');
const { MongoClient } = require('mongodb');

const app = express();
const port = 8002;

const dbName = process.env.DB_NAME;
const dbCollection = process.env.DB_COLLECTION;
const dbUser = process.env.DB_USER;
const dbPassword = process.env.DB_PASSWORD;
const dbHost = process.env.DB_HOST || 'mongodb'; // Default to 'localhost' if not specified
const dbPort = process.env.DB_PORT || '27017'; // Default to '27017' if not specified

const mongoUri = `mongodb://${dbUser}:${dbPassword}@${dbHost}:${dbPort}/${dbName}`;


app.use(express.json());

app.get('/results', async (req, res) => {
    const { userid, password } = req.body;
    if (!userid || !password) {
        return res.status(400).json({ error: "Missing userid or password" });
    }

    try {
        const authResponse = await axios.post('http://authentication-service:8000/validate', {
            userid,
            password
        });

        if (authResponse.status !== 200) {
            return res.status(401).json({ error: "Invalid credentials" });
        }

        const client = new MongoClient(mongoUri);
        await client.connect();
        const db = client.db(dbName);
        const collection = db.collection(dbCollection);

        const results = await collection.find({ userid }).toArray();
        client.close();

        res.json(results);
    } catch (error) {
        res.status(500).json({ error: "An error occurred" });
    }
});

app.listen(port, () => {
    console.log(`Show Results app listening at http://localhost:${port}`);
});