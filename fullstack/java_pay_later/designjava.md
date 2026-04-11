### Java implementation design for LazyPay (Spring Boot + MongoDB)

This document maps `design.md` to a Java stack using Spring Boot 3.x (Java 17+). It includes framework choices, package layout, Mongo models/indexes, transactions, idempotency, DTO validation, controllers, error handling, observability, and testing.

### Core stack
- **Framework**: Spring Boot 3.x
- **Web/API**: spring-boot-starter-web (or WebFlux if reactive)
- **MongoDB**: spring-boot-starter-data-mongodb
- **Validation**: Jakarta Bean Validation (Hibernate Validator)
- **Docs**: springdoc-openapi (UI + OpenAPI)
- **Observability**: Micrometer + Prometheus; OpenTelemetry (optional)
- **Logging**: SLF4J + Logback
- **Migrations/Indexes (optional)**: Mongock
- **Testing**: JUnit 5, Spring Boot Test, Testcontainers (MongoDB)

### Dependencies (Maven)
```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-dependencies</artifactId>
      <version>3.3.2</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
  </dependencyManagement>

<dependencies>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
  </dependency>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-mongodb</artifactId>
  </dependency>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
  </dependency>
  <dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.5.0</version>
  </dependency>
  <dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
  </dependency>
  <!-- Optional -->
  <dependency>
    <groupId>io.mongock</groupId>
    <artifactId>mongock-springboot</artifactId>
    <version>5.4.2</version>
  </dependency>
  
  <!-- Test -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
  </dependency>
  <dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>mongodb</artifactId>
    <version>1.20.1</version>
    <scope>test</scope>
  </dependency>
</dependencies>
```

### Configuration
```yaml
# src/main/resources/application.yml
spring:
  data:
    mongodb:
      uri: ${MONGODB_URI:mongodb://localhost:27017}
      database: ${MONGODB_DB:lazypay}
  mvc:
    problemdetails:
      enabled: true
server:
  port: ${PORT:8080}
  servlet:
    context-path: /api/v1
management:
  endpoints:
    web:
      exposure:
        include: prometheus,health,info
  metrics:
    tags:
      application: lazypay
```

### Package layout
```
com.lazypay
  ├─ api (controllers)
  │   ├─ UsersController
  │   ├─ MerchantsController
  │   ├─ TransactionsController
  │   └─ ReportsController
  ├─ domain (entities/enums)
  │   ├─ users (User, UserBalance)
  │   ├─ merchants (Merchant, MerchantFeeHistory)
  │   └─ transactions (Transaction, TransactionType, TransactionStatus, Currency)
  ├─ dto (requests/responses)
  ├─ repository (Spring Data interfaces)
  ├─ service (UserService, MerchantService, PurchaseService, PaymentService, ReportingService)
  ├─ config (Mongo config, transactions, CORS, OpenAPI)
  └─ exception (domain exceptions + @ControllerAdvice)
```

### Mongo entities and indexes
- Use `@Document(collection="...")` and `@Indexed`/`@CompoundIndexes`.
- Use `@Version` on `UserBalance.version` for optimistic concurrency.
- Create unique indexes: `users.email`, `merchants.name`, `transactions(userId, idempotencyKey)` or use a dedicated `idempotency_keys` with TTL.

```java
// users
@Document("users")
@CompoundIndexes({ @CompoundIndex(name = "status_idx", def = "{'status': 1}") })
public class User {
  @Id private ObjectId id;
  @NotBlank private String name;
  @Email @Indexed(unique = true) private String email;
  @PositiveOrZero private double creditLimit;
  @NotNull private UserStatus status = UserStatus.ACTIVE;
  private Instant createdAt = Instant.now();
  private Instant updatedAt = Instant.now();
}

@Document("user_balances")
public class UserBalance {
  @Id private ObjectId id;
  @Indexed(unique = true) private ObjectId userId;
  @PositiveOrZero private double outstandingAmount = 0.0;
  private double totalPurchases = 0.0;
  private double totalPayments = 0.0;
  @Version private Long version; // optimistic concurrency
  private Instant updatedAt = Instant.now();
}

// merchants
@Document("merchants")
public class Merchant {
  @Id private ObjectId id;
  @Indexed(unique = true) @NotBlank private String name;
  @DecimalMin("0.0") @DecimalMax("100.0") private double currentFeePct;
  private Instant createdAt = Instant.now();
  private Instant updatedAt = Instant.now();
}

@Document("merchant_fee_history")
@CompoundIndex(name = "merchant_eff_desc", def = "{'merchantId': 1, 'effectiveFrom': -1}")
public class MerchantFeeHistory {
  @Id private ObjectId id;
  @Indexed private ObjectId merchantId;
  private double feePct;
  private Instant effectiveFrom;
  private String changedBy;
  private Instant createdAt = Instant.now();
}

// transactions
@Document("transactions")
@CompoundIndexes({
  @CompoundIndex(name = "user_created", def = "{'userId': 1, 'createdAt': -1}"),
  @CompoundIndex(name = "merchant_created", def = "{'merchantId': 1, 'createdAt': -1}"),
  @CompoundIndex(name = "type_created", def = "{'type': 1, 'createdAt': -1}"),
  @CompoundIndex(name = "user_idem", def = "{'userId': 1, 'idempotencyKey': 1}", unique = true, sparse = true)
})
public class Transaction {
  @Id private ObjectId id;
  @NotNull private TransactionType type;
  @Indexed @NotNull private ObjectId userId;
  private ObjectId merchantId; // nullable for PAYMENT
  @Positive double amount;
  @NotNull private Currency currency = Currency.INR;
  @NotNull private TransactionStatus status;
  private Double appliedFeePct; // PURCHASE
  private Double feeAmount;     // PURCHASE
  private Double merchantPayoutAmount; // PURCHASE
  private Double balanceBefore;
  private Double balanceAfter;
  private String idempotencyKey;
  private String reason;
  private Instant createdAt = Instant.now();
  private Map<String,Object> metadata;
}

@Document("idempotency_keys")
@CompoundIndex(name = "scope_key", def = "{'scope': 1, 'key': 1}", unique = true)
@org.springframework.data.mongodb.core.index.TTLIndex(name = "ttl_idx", expireAfterSeconds = 259200)
public class IdempotencyKey {
  @Id private ObjectId id;
  private String scope; // userId or global
  private String key;
  private String responseHash;
  private Instant createdAt = Instant.now();
  @Indexed(expireAfterSeconds = 259200) private Instant ttlExpiresAt; // alternative TTL
}
```

### Repositories (Spring Data)
```java
public interface UserRepository extends MongoRepository<User, ObjectId> {
  Optional<User> findByEmail(String email);
}
public interface UserBalanceRepository extends MongoRepository<UserBalance, ObjectId> {
  Optional<UserBalance> findByUserId(ObjectId userId);
}
public interface MerchantRepository extends MongoRepository<Merchant, ObjectId> {
  Optional<Merchant> findByName(String name);
}
public interface MerchantFeeHistoryRepository extends MongoRepository<MerchantFeeHistory, ObjectId> {
  List<MerchantFeeHistory> findByMerchantIdOrderByEffectiveFromDesc(ObjectId merchantId);
}
public interface TransactionRepository extends MongoRepository<Transaction, ObjectId> {
  Page<Transaction> findByUserId(ObjectId userId, Pageable pageable);
}
public interface IdempotencyKeyRepository extends MongoRepository<IdempotencyKey, ObjectId> {
  Optional<IdempotencyKey> findByScopeAndKey(String scope, String key);
}
```

### Transactions and session config
- Requires MongoDB replica set.
- Provide `MongoTransactionManager` and use `@Transactional` around purchase/payment.

```java
@Configuration
public class MongoTxConfig {
  @Bean
  MongoTransactionManager transactionManager(MongoDatabaseFactory dbFactory) {
    return new MongoTransactionManager(dbFactory);
  }
}
```

### Services (business logic)
- **UserService**: onboard user (unique email), fetch profile + dues, update.
- **MerchantService**: create merchant, update fee (append fee history), get fee/history.
- **PurchaseService**: validate user/merchant active; compute fee; enforce limit; in transaction: insert transaction, increment balance; reserve idempotency.
- **PaymentService**: validate amount; in transaction: insert transaction, decrement balance; idempotency.
- **ReportingService**: aggregations via `Aggregation` framework.

```java
@Service
public class PurchaseService {
  private final TransactionRepository txRepo;
  private final UserRepository userRepo;
  private final UserBalanceRepository balRepo;
  private final MerchantRepository merchantRepo;
  private final IdempotencyKeyRepository idemRepo;

  @Transactional
  public Transaction purchase(PurchaseRequest req) {
    var user = userRepo.findById(req.userId()).orElseThrow(() -> new UserNotFound(req.userId()));
    var bal = balRepo.findByUserId(req.userId()).orElseThrow();
    var merchant = merchantRepo.findById(req.merchantId()).orElseThrow(() -> new MerchantNotFound(req.merchantId()));

    double available = Math.max(0, user.getCreditLimit() - bal.getOutstandingAmount());
    if (req.amount() > available) throw new CreditLimitExceeded(req.userId(), req.amount(), available);

    if (req.idempotencyKey() != null) {
      idemRepo.findByScopeAndKey(req.userId().toHexString(), req.idempotencyKey())
              .ifPresent(k -> { throw new DuplicateRequest(req.idempotencyKey()); });
      idemRepo.save(new IdempotencyKey(null, req.userId().toHexString(), req.idempotencyKey(), null, Instant.now(), Instant.now().plus(3, ChronoUnit.DAYS)));
    }

    double feePct = merchant.getCurrentFeePct();
    double fee = round(req.amount() * feePct / 100.0, 2);
    double payout = round(req.amount() - fee, 2);

    var tx = new Transaction();
    tx.setType(TransactionType.PURCHASE);
    tx.setUserId(req.userId());
    tx.setMerchantId(req.merchantId());
    tx.setAmount(req.amount());
    tx.setCurrency(req.currency());
    tx.setStatus(TransactionStatus.APPROVED);
    tx.setAppliedFeePct(feePct);
    tx.setFeeAmount(fee);
    tx.setMerchantPayoutAmount(payout);
    tx.setBalanceBefore(bal.getOutstandingAmount());
    tx.setBalanceAfter(round(bal.getOutstandingAmount() + req.amount(), 2));
    tx.setIdempotencyKey(req.idempotencyKey());

    txRepo.save(tx);
    bal.setOutstandingAmount(bal.getOutstandingAmount() + req.amount());
    bal.setTotalPurchases(bal.getTotalPurchases() + req.amount());
    balRepo.save(bal); // version field enforces optimistic concurrency

    return tx;
  }
}
```

### DTOs and validation
```java
public record CreateUserRequest(@NotBlank String name, @Email String email, @PositiveOrZero double creditLimit) {}
public record UpdateUserRequest(String name, @PositiveOrZero Double creditLimit, UserStatus status) {}
public record PurchaseRequest(ObjectId userId, ObjectId merchantId, @Positive double amount, Currency currency, String idempotencyKey) {}
public record PaymentRequest(ObjectId userId, @Positive double amount, Currency currency, String idempotencyKey) {}
```

### Controllers (REST endpoints)
- Map exactly as in `design.md` under `/api/v1` context-path.
- Use `@RestController`, `@RequestMapping("/users")`, etc. Return DTOs; map domain exceptions to HTTP.

```java
@RestController
@RequestMapping("/users")
public class UsersController {
  private final UserService service;
  @PostMapping public ResponseEntity<UserCreatedResponse> create(@Valid @RequestBody CreateUserRequest req) { ... }
  @GetMapping("/{id}") public UserResponse get(@PathVariable ObjectId id) { ... }
  @GetMapping public Page<UserResponse> list(@RequestParam Optional<Boolean> reachedLimit, Pageable pageable) { ... }
}
```

### Error handling
- Define domain exceptions (`UserNotFound`, `DuplicateEntity`, `CreditLimitExceeded`, `InvalidAmount`, etc.).
- Centralize with `@ControllerAdvice` and `@ExceptionHandler` mapping to HTTP status codes per design.

### Reporting (aggregations)
- Use Spring Data Mongo `Aggregation` for:
  - Merchant fee collected: match PURCHASE/APPROVED + merchantId + date range, group sum `feeAmount`.
  - User dues: read from `user_balances`.
  - Users at/over limit: `$lookup` users + balances with `$expr` compare.
  - Total dues: sum `user_balances.outstandingAmount`.

### Observability
- Micrometer Prometheus endpoint at `/actuator/prometheus`.
- OpenTelemetry Java Agent (optional) for traces: `-javaagent:opentelemetry-javaagent.jar` with OTLP exporter.
- Structured logs via Logback JSON encoder (optional).

### CORS and OpenAPI
- Configure CORS via `WebMvcConfigurer`.
- springdoc-openapi exposes docs at `/swagger-ui.html` and `/v3/api-docs`.

### Testing strategy
- Unit tests for services with Mockito.
- Slice tests for controllers (`@WebMvcTest`).
- Integration tests using Testcontainers MongoDB and full Spring Boot context for transaction paths (purchase/payment).

### Migrations and index creation
- Option A: rely on `spring.data.mongodb.auto-index-creation=true` (dev) and pre-create in prod.
- Option B: **Mongock** changelogs to create indexes and seed reference data.

```java
@ChangeUnit(id="init-indexes", order = "001")
public class InitIndexes {
  @Execution
  public void execute(MongoTemplate template) {
    template.indexOps("users").ensureIndex(new Index().on("email", Sort.Direction.ASC).unique());
    template.indexOps("user_balances").ensureIndex(new Index().on("userId", Sort.Direction.ASC).unique());
    // ... other indexes per design
  }
}
```

### Run locally
1. Start MongoDB replica set (docker-compose or local rsInitiate).
2. `mvn spring-boot:run` (or build a jar and `java -jar`).
3. Visit `/swagger-ui.html` and test endpoints.

### Alternatives
- **Reactive**: Spring WebFlux + ReactiveMongoRepository; use `ReactiveMongoTransactionManager` and reactor types.
- **Framework alternatives**: Micronaut or Quarkus provide similar modules with lower footprint; adapt annotations and DI accordingly.


