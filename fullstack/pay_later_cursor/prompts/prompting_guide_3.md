## 1. Few-Shot Prompts

**Use when:** You want Claude to mirror a pattern (routers, models, tests, React pages).

### Template

```YAML
You are a senior {role}. Follow the pattern from the examples.
- Stack: FastAPI (Pydantic v2, Motor), MongoDB, React+Vite+TS, JWT, Pytest.
- Output ONLY the files I list, no commentary.
- Conventions: {conventions}

Examples:
[EX1: brief input -> exact file output(s)]
[EX2: brief input -> exact file output(s)]

Task:
{new task and file list}
```

### 1: Backend Router Pattern

```YAML
You are a senior FastAPI engineer. Follow the examples.

Examples:
[EX1: Create GET /health -> app/routes/health.py exporting router]
[EX2: Create POST /echo -> app/routes/echo.py returning payload]

Task:
Create POST /users and POST /merchants with validation + Mongo insert using Motor.
Files:
- app/routes/users.py
- app/routes/merchants.py
- app/db/client.py
Constraints:
- Pydantic v2 models, async Motor client, 422 on validation errors.
```

### 2: Report Endpoints Pattern

```YAML
You are a senior FastAPI engineer. Follow the examples.

Examples:
[EX1: GET /reports/ping -> app/routes/reports.py returns {"ok": true}]
[EX2: GET /reports/today -> returns {"date": "<iso>"}]

Task:
Create:
- GET /reports/fee/{merchant_name}
- GET /reports/dues/{user_name}
- GET /reports/users-at-credit-limit
- GET /reports/total-dues
Files:
- app/routes/reports.py
- app/services/reports.py
- app/models/report.py
```

### 3: React Page Pattern

```YAML
You are a senior React engineer. Follow examples.

Examples:
[EX1: Form page -> POST /users, optimistic UI, zod validation]
[EX2: Table -> GET /reports/total-dues, loading/error states]

Task:
Create "Transactions" page:
- Form: user_name, merchant_name, amount (number)
- On submit -> POST /transactions
- Show last 10 transactions with status
Files:
- web/src/pages/Transactions.tsx
- web/src/api/client.ts
- web/src/types.ts
```

### 4: Pytest Service Tests Pattern

```YAML
You are a senior Python test engineer. Follow examples.

Examples:
[EX1: Unit test for fee calc]
[EX2: Unit test for credit-limit reject]

Task:
Add tests for:
- Partial payback reduces dues correctly
- Users-at-credit-limit list is accurate
Files:
- tests/test_paybacks.py
- tests/test_reports.py
```

---

## 2. Chain-of-Thought (CoT) Prompts

**Use when:** Designing schemas, fee math, idempotency, tricky API logic.

### Template

```YAML
Let's think step by step:
1) Restate goal
2) List constraints
3) Enumerate edge cases
4) Propose design
5) Produce code in files: {files}
Return only code blocks per file.

Task: {task}
```

### 1: Transaction Processing Logic

```YAML
Let's think through the transaction processing step by step:

Step 1: Validate Input
- Check if user exists in database
- Check if merchant exists in database
- Validate amount > 0

Step 2: Credit Limit Check
- Get user's current dues from transactions
- Calculate: current_dues + new_amount
- Compare with user's credit_limit
- If exceeds, reject transaction

Step 3: Process Transaction
- Calculate merchant fee: amount * (merchant.fee_percentage / 100)
- Amount to pay merchant: amount - fee
- Snapshot fee% into transaction
- Create transaction record (idempotent via requestId)
- Update aggregates if precomputing

Step 4: Return Response
- Success: {"status":"success"}
- Failure: {"status":"rejected","reason":"credit limit"}

Now implement this logic in FastAPI with proper error handling.
Files:
- app/routes/transactions.py
- app/services/transactions.py
- app/repos/transactions_repo.py
- app/models/transaction.py
```

### 2: Payback Logic

```YAML
Think step by step:
Goal: Implement POST /paybacks (partial/full), update outstanding dues, return remaining_dues.
Constraints: no negative amounts; idempotent by requestId; Decimal for money; paise as int.
Edge cases: overpayment returns error; zero amount invalid; concurrent paybacks.

Design: service layer does read-modify-write with optimistic retry.
Files:
- app/routes/paybacks.py
- app/services/paybacks.py
- app/repos/paybacks_repo.py
```

### 3: Mongo Schemas & Indexes

```YAML
Think step by step:
Goal: Define Mongo collections and indexes.
Constraints: unique user.name, unique user.email, unique merchant.name, fast lookups.

Design: users, merchants, transactions, paybacks collections.
Indexes: unique(name/email), tx by user, tx by merchant, paybacks by user, unique(requestId).
Files:
- app/db/indexes.py
- app/models/user.py
- app/models/merchant.py
- app/models/transaction.py
- app/models/payback.py
```

---

## 3. Tree-of-Thought (ToT) Prompts

**Use when:** Evaluating alternative designs; choose the best branch before coding.

### Template

```YAML
Explore 3 solution branches (A/B/C). For each: pros/cons, complexity, risks.
Pick one and justify. Then implement files: {files}. Output only code.
Goal: {goal}
Constraints: {constraints}
```

### 1: Fee Handling Strategy

```YAML
Explore:
A) Fee stored on merchant & snapshot into each transaction
B) Separate fee_history; resolve by tx timestamp
C) Always use current fee (risk: retroactive changes)

Pick best and implement POST /transactions + models.
Files:
- app/models/merchant.py
- app/models/transaction.py
- app/services/transactions.py
```

### 2: Dues Computation Strategy

```YAML
Explore:
A) Pre-aggregate user dues
B) Compute on read from ledger
C) Event-sourced ledger with projections

Pick best for simplicity+accuracy. Implement GET /reports/dues/{user_name}.
Files:
- app/services/reports.py
- app/repos/transactions_repo.py
```

### 3: Users-at-Credit-Limit Detection

```YAML
Explore:
A) Compute dynamically
B) Maintain boolean flag updated on every txn/payback
C) Nightly materialization job

Pick best, implement endpoint.
Files:
- app/routes/reports.py
- app/services/reports.py
```

### 4: Frontend State Strategy

```YAML
Explore:
A) React Query
B) Minimal custom fetch hooks
C) Redux Toolkit

Pick best for Vite+TS baseline. Implement users & merchants forms + lists.
Files:
- web/src/api/client.ts
- web/src/hooks/useUsers.ts
- web/src/pages/Users.tsx
- web/src/pages/Merchants.tsx
```

---

## 4. Graph-of-Thought (GoT) Prompts

**Use when:** Parallelize subproblems; define dependencies; merge outputs.

### Template

```YAML
Build a dependency graph:
Nodes: {nodes}
Edges: {edges}
Plan parallelizable tasks; then output artifacts per node in order.
Files: {files}
Task: {task}
```

### 1: End-to-End MVP Graph

```YAML
Nodes: models, db client, users route, merchants route, tx route, paybacks route, reports route, tests
Edges: routes -> models/db; tests -> services

Implement in order.
Files:
- app/db/client.py
- app/models/*.py
- app/routes/*.py
- tests/test_*.py
```

### 2: Reporting Graph

```YAML
Nodes: tx aggregation service, dues calculator, fee report, users-at-limit, total-dues
Edges: reports -> aggregators -> repos

Implement with shared aggregator utils.
Files:
- app/services/aggregators.py
- app/services/reports.py
- app/routes/reports.py
```

### 3: Frontend Graph

```YAML
Nodes: API client, types, Users page, Merchants page, Transactions page, Reports pages
Edges: pages -> api client -> backend

Implement minimal nav + four pages.
Files:
- web/src/api/client.ts
- web/src/types.ts
- web/src/pages/{Users,Merchants,Transactions,Reports}.tsx
```

---

## 5. ReAct (Reason + Act) Prompts

**Use when:** Iterative fixes, bug hunts, stepwise edits.

### Template

```YAML
Reason:
- Brief plan (3–5 bullets)

Act:
- Create/modify files: {files}

Constraints: {constraints}
Return only file outputs; keep "Reason" under 5 bullets.
Task: {task}
```

### 1: PATCH Merchant Fee

```YAML
Reason:
- Add route param
- Validate percentage
- Update doc
- Add unit test

Act:
Files:
- app/routes/merchants.py (PATCH /merchants/{merchant_name})
- tests/test_merchants.py
```

### 2: Idempotent Transactions

```YAML
Reason:
- Add requestId
- Unique index
- Upsert with safe retry
- Return existing tx on duplicate

Act:
Files:
- app/models/transaction.py
- app/repos/transactions_repo.py
- app/routes/transactions.py
- tests/test_idempotency.py
```

### 3: Fix Rounding Bug

```YAML
Reason:
- Use Decimal helpers
- Store paise as int
- Quantize to 0.01

Act:
Files:
- app/utils/money.py
- app/services/transactions.py
- tests/test_money.py
```

### 4: React Optimistic UI

```YAML
Reason:
- Show pending state
- Rollback on error
- Toast messages

Act:
Files:
- web/src/pages/Transactions.tsx
- web/src/api/client.ts
```

---

## 6. Plan-and-Execute (PaE) Prompts

**Use when:** Larger features spanning BE+FE+Tests.

### Template

```YAML
Phase 1 – PLAN: Output a 6–10 step plan only.
Phase 2 – EXECUTE: Implement steps in files: {files}. No commentary.

Task: {task}
```

### 1: Implement All Core Endpoints

```YAML
Phase 1 – PLAN (steps for users, merchants, tx, paybacks, reports)
Phase 2 – EXECUTE
Files: app/** (routes, services, models, repos), tests/**
```

### 2: Auth/JWT

```YAML
Phase 1 – PLAN (login, signup, middleware, protected routes)
Phase 2 – EXECUTE
Files:
- app/routes/auth.py
- app/middleware/auth.py
- web/src/auth/**
```

### 3: Docker & Compose

```YAML
Phase 1 – PLAN (Dockerfiles, docker-compose, env)
Phase 2 – EXECUTE
Files:
- Dockerfile.api
- Dockerfile.web
- docker-compose.yml
- .env.example
```

---

## 7. Skeleton-to-Concrete Prompts

**Use when:** Contracts stable; implementation TBD. Generate stubs, then fill.

### Template

```YAML
Step A (Skeleton): Emit file trees + empty functions/schemas.
Step B (Concrete): Replace TODOs with working code and tests.

Task & Files: {task/files}
```

### 1: Reports Module

```YAML
Step A: Skeleton for aggregators + reports routes
Step B: Fill logic + tests
Files:
- app/services/aggregators.py
- app/services/reports.py
- tests/test_reports.py
```

### 2: Paybacks Module

```YAML
Skeleton then fill:
Files:
- app/routes/paybacks.py
- app/services/paybacks.py
- tests/test_paybacks.py
```

### 3: React Pages

```YAML
Skeleton then fill:
Files:
- web/src/pages/{Users,Merchants,Transactions,Reports}.tsx
- web/src/router.tsx
```

---

## 8. Test-Driven Development (TDD) Prompts

**Use when:** Critical calculations & regressions.

### Template

```YAML
Write tests first for {behavior}. Then implement to pass.
Files: tests/* then app/*.
Constraints: pytest-asyncio where needed.
```

### 1: Fee Collection Tests First

```YAML
Tests: fee is snapshot at tx time; Decimal math; rounding rules.
Files: tests/test_fee_calc.py → app/services/transactions.py
```

### 2: Credit Limit Tests First

```YAML
Tests: reject over-limit; allow exactly at limit; multi-tx accumulation.
Files: tests/test_credit_limit.py → app/services/transactions.py
```

### 3: Partial Payback Tests First

```YAML
Tests: partial reduces dues; multiple paybacks; zero/negative invalid.
Files: tests/test_paybacks.py → app/services/paybacks.py
```

---

## 9. Spec-then-Implement (OpenAPI) Prompts

**Use when:** Team alignment; FE/QA parallelization.

### Template

```YAML
Produce openapi.yaml for endpoints. Then generate server stubs + TS types.
Files: openapi.yaml, app/routes/*, web/src/types/api.ts
Task: {scope}
```

### 1: Core Endpoints Spec

```YAML
Create openapi.yaml for users/merchants/transactions/paybacks/reports,
then generate FastAPI stubs + TS types.
```

### 2: Error Models in Spec

```YAML
Extend spec with error shapes (422/404/409), then implement handlers & tests.
```

### 3: Auth Spec

```YAML
Add JWT security scheme; protect POST /transactions & POST /paybacks.
Implement middleware + 401 responses.
```

---

## 10. Rubric-Driven Critic (Reflexion) Prompts

**Use when:** Quality pass before commit.

### Template

```YAML
Rubric (0–5): Correctness, Safety, Tests, DX, Performance, Readability.
1) Critique current files {files}
2) List prioritized fixes
3) Apply fixes, output patched files only
```

### 1: Transactions Service Audit

```YAML
Apply rubric to: app/services/transactions.py, app/repos/transactions_repo.py
Propose fixes; output patches only.
```

### 2: Reports Efficiency Audit

```YAML
Apply rubric to: app/services/reports.py (indexes, pipelines, N+1 risks)
Propose fixes; output patches only.
```

### 3: React Accessibility Audit

```YAML
Apply rubric to: forms/pages; ensure labels, aria, keyboard nav.
Propose fixes; output patches only.
```

---

## 11. Self-Consistency (N-Best & Vote) Prompts

**Use when:** Non-obvious algorithms or design choices.

### Template

```YAML
Generate 3 variants (V1–V3) for {problem}.
Compare vs: simplicity, accuracy, extensibility.
Select one; implement in files: {files}.
```

### 1: Dues Aggregation Plan

```YAML
Variants: precompute vs on-read vs hybrid projections.
Pick one; implement GET /reports/dues/{user_name}.
```

### 2: Fee Rounding Policy

```YAML
Variants: bankers rounding, floor to paise, Decimal quantize.
Pick one; implement helpers + tests.
Files:
- app/utils/money.py
- tests/test_money.py
```

### 3: React Data Layer

```YAML
Variants: custom hooks vs React Query vs RTK Query.
Pick one; implement API client + hooks.
```

---

## 12. Strict JSON / Schema-Constrained Prompts

**Use when:** Configs, seeds, CI artifacts.

### Template

```YAML
Output ONLY valid {format} with no comments.
Schema: {short schema}
Task: {config/manifest/seed}
```

### 1: Seed Data

```YAML
Output ONLY valid JSON array for initial merchants (name, fee_percentage)
and users (name, email, credit_limit).
```

### 2: docker-compose

```YAML
Output ONLY valid YAML for services: api, web, mongo, mongo-express.
Include ports, env, volumes, depends_on.
```

### 3: Kubernetes Manifests

```YAML
Output ONLY valid YAML: Deployment/Service for api+web, Secret, ConfigMap.
Minimal, production-safe defaults.
```

---

## 13. Tool / Action-Oriented (Cursor File Ops) Prompts

**Use when:** Surgical multi-file edits; small diffs applied cleanly.

### Template

```YAML
Create/overwrite exactly these files:
- {file list}

Each file in its own code block. No extra text.
Task: {task}
```

### 1: Money Utils

```YAML
Files:
- app/utils/money.py
- tests/test_money.py
Task: Decimal/paise helpers + tests.
```

### 2: Add requestId to Transactions

```YAML
Files:
- app/models/transaction.py
- app/repos/transactions_repo.py
- tests/test_idempotency.py
```

### 3: React Router & Nav

```YAML
Files:
- web/src/router.tsx
- web/src/App.tsx
- web/src/components/Nav.tsx
```

---

## 14. Docstring-Driven Development (DDD) Prompts

**Use when:** Service functions & utils; ensure clarity via contracts.

### Template

```YAML
For each function, write a precise docstring incl. preconditions,
postconditions, and examples. Then implement.

Files: {files}
Task: {task}
```

### 1: transactions.service

```YAML
Functions: create_transaction, compute_fee, check_credit.
Docstrings first; implement next; add unit tests.
```

### 2: paybacks.service

```YAML
Functions: apply_payback, remaining_dues.
Docstrings first; implement next; add unit tests.
```

### 3: reports.service

```YAML
Functions: fee_collected_for_merchant, users_at_credit_limit, total_dues.
Docstrings first; implement next; add unit tests.
```

---

## 15. Decomposition-by-Artifact (Back/Front/DevOps Triad) Prompts

**Use when:** Coordinating multiple artifacts in parallel.

### Template

```YAML
Produce 3 sections with files:
A) Backend {files}
B) Frontend {files}
C) DevOps {files}
Keep each section self-contained.

Task: {feature}
```

### 1: MVP Slice (Users + Merchants)

```YAML
A) Backend: routes/models/repos/tests
B) Frontend: forms + list pages
C) DevOps: compose + env
```

### 2: Transactions Feature

```YAML
A) Backend: POST /transactions (idempotent, Decimal)
B) Frontend: Transactions page + history list
C) DevOps: seed scripts
```

### 3: Reports Feature

```YAML
A) Backend: all /reports/*
B) Frontend: Reports dashboard
C) DevOps: load test config (locustfile.py)
```

---

## Bonus: Mini Drop-Ins

### Rounding Correctness

```YAML
Use Decimal everywhere; store paise as integers; quantize to 0.01; no float math.
```

### Idempotency

```YAML
Add requestId to POST /transactions; unique index; on retry return existing tx.
```

### Validation

```YAML
Use Pydantic v2 validators; 422 on invalid email/percentage; strict types.
```

---

## Global Vibe-Coding Preamble (Paste Once)

```YAML
You are Claude Sonnet 4 acting as a principal engineer.
Stack: FastAPI (Python 3.11, Pydantic v2, Motor), MongoDB, React (Vite+TS).
Non-negotiables: async I/O, Decimal for money, paise-as-int storage, idempotent POST /transactions, pytest.
Style: small, composable modules; pure functions; clear typing; docstrings; full parity with API spec.
Outputs: Only the files requested, one code block per file, no prose.
```
