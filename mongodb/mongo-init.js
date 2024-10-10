db = db.getSiblingDB('aggre-data');

db.createUser({
  user: process.env.MONGO_WRITER_USERNAME,
  pwd: process.env.MONGO_WRITER_PASSWORD,
  roles: [{ role: 'readWrite', db: 'aggre-data' }]
});

db.createUser({
  user: process.env.MONGO_READER_USERNAME,
  pwd: process.env.MONGO_READER_PASSWORD,
  roles: [{ role: 'read', db: 'aggre-data' }]
});

db.createCollection('processed-data');