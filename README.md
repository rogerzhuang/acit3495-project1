To build:
    docker-compose up --build

To test:
    Authentication service:
        curl -X POST http://localhost:8000/validate \
             -H "Content-Type: application/json" \
             -d '{"userid": "user1", "password": "password1"}'
    Enter data service:
        curl -X POST http://localhost:8001/enter-data \
             -H "Content-Type: application/json" \
             -d '{"userid": "user1", "password": "password1", "value": 42.5}'
    Show results service:
        curl -X GET http://localhost:8002/results \
             -H "Content-Type: application/json" \
             -d '{"userid": "user1", "password": "password1"}'