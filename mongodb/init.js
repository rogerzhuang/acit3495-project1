db = db.getSiblingDB('analyticsdb');

db.createUser({
  user: 'reader',
  pwd: process.env.MONGO_PASSWORD_READER,
  roles: [{ role: 'read', db: 'analyticsdb' }]
});

db.createUser({
  user: 'writer',
  pwd: process.env.MONGO_PASSWORD_WRITER,
  roles: [{ role: 'readWrite', db: 'analyticsdb' }]
});

db.createCollection('analytics');
db.analytics.createIndex({ timestamp: 1 }, { expireAfterSeconds: 86400 });  // Optional: Create a TTL index to automatically delete old data after 24 hours
