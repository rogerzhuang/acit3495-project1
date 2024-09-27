const express = require('express');
const axios = require('axios');
const { MongoClient } = require('mongodb');

const app = express();
const port = 8002;

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

        const client = new MongoClient('mongodb://mongodb:27017');
        await client.connect();
        const db = client.db('analyticsdb');
        const collection = db.collection('analytics');

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