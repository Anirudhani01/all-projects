# LazyPay (Spring Boot + MongoDB)

This project was scaffolded from `designjava.md`.

## Prerequisites
- Java 17+
- Maven 3.9+
- MongoDB (replica set for transactions)

## Run locally
1. Start MongoDB (replica set recommended)
2. Build and run:
   ```bash
   mvn spring-boot:run
   ```
3. Open Swagger UI:
   - http://localhost:8080/swagger-ui.html

## Notes
- Project layout follows the design document (controllers, services, domain, DTOs, repositories, config, exception).
- `MongoTransactionManager` is provided. Ensure your MongoDB is a replica set for transactions to work.
