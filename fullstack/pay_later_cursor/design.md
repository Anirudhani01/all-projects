design.md file  I’m going to design a modular-monolithic FastAPI + MongoDB architecture for a Pay-Later service, step-by-step: database design first, then service segregation, then REST endpoints, then validation/error strategy. No code generated, as requested.

### Database design (MongoDB): collections, schema, indexes
- users
  - Fields:
    - _id (ObjectId)
    - name (string)
    - email (string, unique)
    - credit_limit (number, non-negative)
    - status (enum: ACTIVE, BLOCKED)
    - created_at (datetime), updated_at (datetime)
  - Indexes:
    - unique on email
    - optional: compound on status
- user_balances
  - Purpose: fast lookup and atomic updates of a user’s outstanding dues
  - Fields:
    - _id (ObjectId)
    - user_id (ObjectId, unique)
    - outstanding_amount (number, >= 0)
    - total_purchases (number)
    - total_payments (number)
    - version (int, optimistic concurrency)
    - updated_at (datetime)
  - Indexes:
    - unique on user_id
    - secondary index on outstanding_amount (to query users at/over limit)
- merchants
  - Fields:
    - _id (ObjectId)
    - name (string, unique)
    - current_fee_pct (number, 0–100)
    - created_at (datetime), updated_at (datetime)
  - Indexes:
    - unique on name
- merchant_fee_history
  - Purpose: audit and reproduce historical fee calculations
  - Fields:
    - _id (ObjectId)
    - merchant_id (ObjectId)
    - fee_pct (number)
    - effective_from (datetime)
    - changed_by (string or ObjectId)
    - created_at (datetime)
  - Indexes:
    - compound on (merchant_id, effective_from desc)
- transactions
  - Purpose: immutable ledger of purchases and payments; authoritative for reports
  - Fields:
    - _id (ObjectId)
    - type (enum: PURCHASE, PAYMENT, REFUND if needed later)
    - user_id (ObjectId)
    - merchant_id (ObjectId, nullable for PAYMENT)
    - amount (number, > 0)
    - currency (string, e.g., INR)
    - status (enum: APPROVED, REJECTED, REVERSED) — record rejections too for audit
    - applied_fee_pct (number, only for PURCHASE)
    - fee_amount (number, only for PURCHASE)
    - merchant_payout_amount (number, only for PURCHASE, amount - fee_amount)
    - balance_before (number, user balance before applying txn)
    - balance_after (number, after applying txn)
    - idempotency_key (string, optional but recommended)
    - reason (string, only for REJECTED/REVERSED)
    - created_at (datetime)
    - metadata (object, optional)
  - Indexes:
    - on user_id, merchant_id, created_at, type
    - unique on (user_id, idempotency_key) to enforce idempotency per user
- idempotency_keys
  - Alternative to unique index; use if keys must outlive old transactions or cross-user uniqueness is required
  - Fields:
    - _id (ObjectId)
    - scope (string, e.g., user_id or global)
    - key (string)
    - response_hash (string or response snapshot, optional)
    - created_at (datetime)
    - ttl_expires_at (datetime)
  - Indexes:
    - unique on (scope, key)
    - TTL on ttl_expires_at
- reporting_daily_aggregates (optional, performance optimization)
  - Purpose: pre-aggregated rollups
  - Fields:
    - _id (ObjectId)
    - date (date)
    - merchant_id (ObjectId)
    - total_fee_amount (number)
    - total_purchases (number)
    - total_payments (number)
    - total_outstanding_snapshot (number, optional)
  - Indexes:
    - compound on (date, merchant_id)

Notes:
- Use MongoDB multi-document transactions (replica set) for atomic updates to transactions + user_balances.
- Store applied_fee_pct and fee_amount on each PURCHASE to ensure correctness despite later fee changes.
- Compute outstanding dues either from transactions or from user_balances (authoritative for online path, reconciled from transactions if needed).

### Service segregation (modular monolith)
- Users module
  - UserService
    - onboard user (validate email uniqueness, create users + initialize user_balances)
    - fetch user details and current dues
    - check limit status (available credit = credit_limit - outstanding_amount)
  - UserRepository
    - CRUD for users and user_balances with versioned updates
  - Input/Output schemas (API layer only; no code now)
- Merchants module
  - MerchantService
    - onboard merchant with fee
    - change fee (append to merchant_fee_history, update current_fee_pct)
    - fetch current fee and fee history
  - MerchantRepository
    - CRUD for merchants, merchant_fee_history
- Transactions module
  - PurchaseService
    - validate user/merchant active
    - fetch fee at time of purchase
    - enforce credit limit atomically
    - write transactions record with applied_fee_pct, fee_amount, merchant_payout_amount
    - increment user_balances.outstanding_amount and total_purchases
    - idempotency: dedupe on (user_id, idempotency_key) or via idempotency_keys
  - PaymentService
    - validate payment amount (> 0, <= outstanding)
    - write transactions record
    - decrement user_balances.outstanding_amount and increment total_payments
    - idempotency handling as above
  - TransactionRepository
    - persisting transactions with sessions
  - BalanceRepository
    - versioned updates or transactional updates to user_balances
  - IdempotencyService (cross-cutting within this module)
    - check-and-create key; replay cached response if needed
- Reports module
  - ReportingService
    - merchant fee collected to date: aggregate sum of fee_amount by merchant_id (filters by date range)
    - user dues so far: read from user_balances or sum transactions
    - users at or over credit limit: filter users joined with user_balances where outstanding_amount >= credit_limit
    - total dues from all users: sum user_balances.outstanding_amount
    - optional: populate and query reporting_daily_aggregates for performance
  - ReportingRepository
    - aggregation pipelines and rollups
- Cross-cutting concerns
  - Validation layer for request DTOs
  - ErrorMapping to map domain exceptions to HTTP status codes
  - Observability hooks (logging, metrics, tracing)
  - AuthN/AuthZ placeholder (out of scope here)

### REST API endpoints (by module)
- Users
  - POST /users
    - body: name, email, credit_limit
    - 201 → user created with initial balance 0
    - 409 if email exists
  - GET /users/{user_id}
    - 200 → user profile + credit limit + current dues (from user_balances)
  - GET /users/{user_id}/dues
    - 200 → { outstanding_amount, available_credit }
  - GET /users?reached_limit=true|false (pagination supported)
    - 200 → list of users filtered by limit status
- Merchants
  - POST /merchants
    - body: name, fee_pct
    - 201 → merchant created
    - 409 if name exists
  - PATCH /merchants/{merchant_id}/fee
    - body: fee_pct
    - 200 → updated, with appended merchant_fee_history
  - GET /merchants/{merchant_id}
    - 200 → merchant details + current_fee_pct
  - GET /merchants/{merchant_id}/fee-history?from&to
    - 200 → entries sorted by effective_from desc
- Transactions
  - POST /transactions/purchase
    - headers: Idempotency-Key (recommended)
    - body: user_id, merchant_id, amount, currency (optional default), idempotency_key (optional if header used)
    - 201 → approved transaction with computed fee_amount, applied_fee_pct, merchant_payout_amount, balance_after
    - 409 → duplicate idempotency key
    - 402 → credit limit exceeded
    - 404 → user or merchant not found
  - POST /transactions/payment
    - headers: Idempotency-Key (recommended)
    - body: user_id, amount, currency, idempotency_key
    - 201 → payment accepted, updated balance_after
    - 400 → amount <= 0 or amount > outstanding
    - 409 → duplicate idempotency key
    - 404 → user not found
  - GET /transactions?user_id&merchant_id&type&from&to&page&size
    - 200 → paginated list of transactions
- Reports
  - GET /reports/merchant-fees?merchant_id&from&to
    - 200 → { merchant_id, total_fee_amount, count, from, to }
  - GET /reports/user-dues?user_id
    - 200 → { user_id, outstanding_amount, available_credit }
  - GET /reports/users-at-limit?page&size
    - 200 → list of { user_id, outstanding_amount, credit_limit } where outstanding >= limit
  - GET /reports/total-dues
    - 200 → { total_outstanding_amount }

### Service responsibilities and transaction boundaries
- Purchase flow (atomic):
  - Resolve user and merchant; get current_fee_pct
  - Compute available_credit = credit_limit - outstanding_amount
  - If amount > available_credit → reject with domain error
  - Within a MongoDB session/transaction:
    - Insert transactions with type=PURCHASE, status=APPROVED, applied_fee_pct, fee_amount, merchant_payout_amount, balance_before, balance_after
    - Update user_balances:
      - outstanding_amount += amount
      - total_purchases += amount
      - increment version
    - Create idempotency record if provided
- Payment flow (atomic):
  - Resolve user
  - Validate 0 < amount <= outstanding_amount
  - Within a MongoDB session/transaction:
    - Insert transactions with type=PAYMENT, status=APPROVED, balance_before, balance_after
    - Update user_balances:
      - outstanding_amount -= amount
      - total_payments += amount
      - increment version
    - Create idempotency record if provided

### Error handling and validation strategy
- Request validation (API layer)
  - Enforce types, required fields, and constraints:
    - fee_pct in [0, 100]
    - credit_limit >= 0
    - transaction amount > 0
    - currency enum or ISO 4217 string (default INR)
  - Normalize: trim strings, lowercase emails
- Domain exceptions → HTTP mapping
  - UserNotFound, MerchantNotFound → 404
  - DuplicateEntity (email/name) → 409
  - DuplicateRequest (idempotency) → 409
  - CreditLimitExceeded → 402
  - InvalidAmount, InvalidFee → 400
  - ConflictUpdate (optimistic lock/version mismatch) → 409 (retryable)
- Consistency
  - Use MongoDB sessions/transactions for cross-collection atomicity
  - Optimistic concurrency with version on user_balances if needed for high-contention updates
- Idempotency
  - Require Idempotency-Key header for POST purchase/payment; scope per user_id
  - Enforce via unique index (user_id, idempotency_key) or dedicated idempotency_keys with TTL
- Observability
  - Structured logs on transactions and fee changes
  - Metrics: transaction counts, rejection rates, outstanding totals, DB latencies
  - Tracing spans: API → Service → Repository → Mongo

### Reporting notes (covering use cases)
- Fee collected from a merchant to date
  - Aggregate over transactions where type=PURCHASE, status=APPROVED, merchant_id=..., sum fee_amount, filter by created_at when date range provided
  - Optional: leverage reporting_daily_aggregates for faster queries
- Dues for a user so far
  - Read user_balances.outstanding_amount (authoritative for online)
- Users who reached credit limit
  - Filter where outstanding_amount >= credit_limit (join users + user_balances)
- Total dues from all users together
  - Sum user_balances.outstanding_amount (or use pre-aggregations)

### Mermaid diagram (modular monolith)
mermaid
flowchart LR
  subgraph API[FastAPI Layer]
    UCtrl[UsersController]
    MCtrl[MerchantsController]
    TCtrl[TransactionsController]
    RCtrl[ReportsController]
  end

  subgraph Domain[Domain Services]
    USvc[UserService]
    MSvc[MerchantService]
    PSvc[PurchaseService]
    PaySvc[PaymentService]
    RSvc[ReportingService]
    Idem[IdempotencyService]
  end

  subgraph Data[Repositories]
    URepo[UserRepository]
    MRepo[MerchantRepository]
    TRepo[TransactionRepository]
    BRepo[BalanceRepository]
    RRepo[ReportingRepository]
    IRepo[IdempotencyRepository]
  end

  subgraph DB[MongoDB]
    users[(users)]
    balances[(user_balances)]
    merchants[(merchants)]
    feehist[(merchant_fee_history)]
    txns[(transactions)]
    idemkeys[(idempotency_keys)]
    aggs[(reporting_daily_aggregates)]
  end

  API --> Domain
  UCtrl --> USvc
  MCtrl --> MSvc
  TCtrl --> PSvc
  TCtrl --> PaySvc
  RCtrl --> RSvc
  PSvc --> Idem
  PaySvc --> Idem

  Domain --> Data
  USvc --> URepo
  MSvc --> MRepo
  PSvc --> TRepo
  PSvc --> BRepo
  PaySvc --> TRepo
  PaySvc --> BRepo
  RSvc --> RRepo
  Idem --> IRepo

  Data --> DB
  URepo --> users
  BRepo --> balances
  MRepo --> merchants
  MRepo --> feehist
  TRepo --> txns
  IRepo --> idemkeys
  RRepo --> txns
  RRepo --> balances
  RRepo --> aggs


### Data access and indexing checklist
- Ensure compound indexes on transactions(user_id, created_at) and transactions(merchant_id, created_at) for listing and reporting.
- Unique constraints: users.email, merchants.name, transactions(user_id, idempotency_key) or idempotency_keys(scope, key).
- Add TTL on idempotency_keys.ttl_expires_at (e.g., 24–72h) to control storage growth.

### Operational safeguards
- Validation prevents payments greater than outstanding; return 400.
- Record rejected purchase attempts with status=REJECTED (reason: credit limit exceeded) for audit.
- Store balance_before/balance_after in each transaction for reconciliation and investigations.
- Support pagination everywhere list endpoints are exposed.
- Soft-delete not needed initially; use status fields and immutability of transactions.

Status update:
- Designed the MongoDB schema with collections, indexes, and atomicity approach; defined service boundaries for a modular monolith; detailed REST endpoints per module; laid out validation, error mapping, idempotency, and reporting; and provided a Mermaid diagram of the architecture.

- Core modules defined: users, merchants, transactions, reports
- Data models listed with fields and indexes for users, user_balances, merchants, merchant_fee_history, transactions, idempotency_keys, reporting_daily_aggregates
- REST endpoints specified for onboarding, fee changes, purchases, payments, and reports to meet all use cases
- Services segregated with clear responsibilities and transaction boundaries; idempotency and concurrency addressed
- Error and validation strategy mapped to HTTP semantics; reporting queries defined for the required metrics