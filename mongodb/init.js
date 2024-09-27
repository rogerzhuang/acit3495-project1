db = db.getSiblingDB('analyticsdb');
db.createCollection('analytics');
db.analytics.createIndex({ timestamp: 1 }, { expireAfterSeconds: 86400 });  // Optional: Create a TTL index to automatically delete old data after 24 hours