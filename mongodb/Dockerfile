FROM mongo:latest

# Copy the initialization script
COPY mongo-init.js /docker-entrypoint-initdb.d/

# Expose the default MongoDB port
EXPOSE 27017

# Use the default entrypoint of the mongo image
CMD ["mongod"]