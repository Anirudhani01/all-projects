# Advanced Prompting Techniques For Backend Engineering

_Naren Allam_, PythonGuru, 2025

## 1. Few-Shot Learning Prompts

### 1: API Endpoint Development
```python
Create FastAPI endpoints following these patterns:

1 - User Creation:
@app.post("/users")
async def create_user(user: UserCreate):
    # Validate credit limit > 0
    # Check if user exists
    # Save to MongoDB
    return {"name": user.name, "credit_limit": user.credit_limit}

2 - Merchant Creation:
@app.post("/merchants")
async def create_merchant(merchant: MerchantCreate):
    # Validate fee_percentage between 0-100
    # Check if merchant exists
    # Save to MongoDB
    return {"name": merchant.name, "fee_percentage": merchant.fee_percentage}

Now create the transaction endpoint following the same pattern for:
POST /transactions with user_name, merchant_name, amount
- Check user credit limit
- Calculate merchant fee
- Update user dues
- Return success/rejection status
```

### 2: MongoDB Schema Design
```json
Follow these MongoDB schema patterns:

User Schema Example:
{
  "_id": ObjectId,
  "name": "user1",
  "email": "u1@email.com",
  "credit_limit": 1000,
  "current_dues": 250,
  "created_at": ISODate
}

Merchant Schema Example:
{
  "_id": ObjectId,
  "name": "merchant1",
  "fee_percentage": 2.5,
  "total_fee_collected": 150.75,
  "updated_at": ISODate
}

Now design the Transaction schema with fields:
- transaction_id, user_name, merchant_name, amount, fee_deducted, status, timestamp
```

### 3: React Component Patterns
```js
Follow these React component patterns:

- User Form Component:
const UserForm = () => {
  const [formData, setFormData] = useState({name: '', email: '', credit_limit: ''});
  const handleSubmit = async (e) => {
    // API call to POST /users
    // Handle success/error
  };
  return <form>{/* form fields */}</form>;
};

- Dashboard Component:
const Dashboard = () => {
  const [users, setUsers] = useState([]);
  useEffect(() => {
    // Fetch users from API
  }, []);
  return <div>{/* display users */}</div>;
};

Now create MerchantManagement component following the same pattern with:
- State for merchants list
- Add/edit merchant functionality
- Fee percentage update feature
```

## 2. Chain-of-Thought (CoT) Prompts

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
- Create transaction record
- Update user's total dues
- Update merchant's collected fees

Step 4: Return Response
- Success: {"status": "success"}
- Failure: {"status": "rejected", "reason": "credit limit"}

Now implement this logic in FastAPI endpoint with proper error handling.
```

### 2: Database Design Reasoning
```YAML
Let's think through the optimal database structure:

Step 1: Identify Entities
- Users (name, email, credit_limit)
- Merchants (name, fee_percentage)
- Transactions (user, merchant, amount, timestamp)

Step 2: Relationship Analysis
- User can have many transactions (1:N)
- Merchant can have many transactions (1:N)
- Need to track user's total dues efficiently

Step 3: Optimization Considerations
- Store calculated fields vs real-time calculation?
- Index on user_name for quick dues lookup
- Index on merchant_name for fee reports

Step 4: Final Schema Decision
- Denormalize user dues for performance
- Keep transaction history for audit trail
- Use compound indexes for reporting queries

Implement this schema with proper MongoDB collections and indexes.
```

### 3: Frontend State Management
```YAML
Let's think through React state management strategy:

Step 1: Identify State Requirements
- User data (for forms and display)
- Merchant data (for transactions and management)
- Transaction history
- Report data

Step 2: State Structure Decision
- Global state vs component state?
- Context API vs prop drilling?
- API response caching strategy?

Step 3: Update Patterns
- Optimistic updates for better UX
- Error rollback mechanisms
- Real-time updates for reports

Step 4: Implementation Plan
- Create React Context for global state
- Custom hooks for API calls
- Error boundary components

Build the state management system following this analysis.
```

## 3. Tree-of-Thought Prompts

### 1: Architecture Decision Tree
```YAML
Design the Pay-Later system architecture by exploring multiple paths:

Branch A: Microservices Architecture
- User Service (FastAPI)
- Merchant Service (FastAPI) 
- Transaction Service (FastAPI)
- Report Service (FastAPI)
- Shared MongoDB

Branch B: Monolithic Architecture
- Single FastAPI Application
- Modular structure by domain
- Shared database models
- Internal service layer

Branch C: Hybrid Approach
- Core API (Users, Merchants, Transactions)
- Separate Reporting Service
- Shared database with read replicas
- Event-driven updates

Evaluate each branch for:
- Development complexity
- Scalability requirements
- Team size considerations
- Deployment complexity

Choose the best approach and implement the initial structure.
```

### 2: Error Handling Strategy Tree
```YAML
Design comprehensive error handling exploring different approaches:

Branch A: Exception-Based Handling
- Custom exception classes
- FastAPI exception handlers
- HTTP status code mapping
- Structured error responses

Branch B: Result Pattern
- Result[T, Error] return types
- Explicit error handling
- No exceptions for business logic
- Functional programming approach

Branch C: Hybrid Approach
- Exceptions for system errors
- Result types for business logic
- Middleware for logging
- Client-friendly error messages

For each branch, consider:
- Code readability
- Error debugging
- API consistency
- Frontend integration

Implement the chosen error handling strategy across the application.
```

### 3: Frontend Component Architecture Tree
```YAML
Design React frontend architecture with multiple approaches:

Branch A: Page-Based Structure
- Pages (Users, Merchants, Transactions, Reports)
- Components (Forms, Tables, Cards)
- Hooks (API calls, state management)
- Utils (formatting, validation)

Branch B: Feature-Based Structure
- Features (User Management, Transaction Processing)
- Shared Components
- Services (API layer)
- Store (Global state)

Branch C: Domain-Driven Structure
- Domains (User, Merchant, Transaction, Report)
- UI Components (per domain)
- Business Logic (per domain)
- Infrastructure (API, storage)

Analyze each for:
- Code organization
- Reusability
- Team collaboration
- Maintenance

Build the frontend following the selected structure.
```

## 4. Graph-of-Thought Prompts

### 1: System Dependencies Graph
```YAML
Map the Pay-Later system as an interconnected graph:

Nodes:
- User Management → [validates] → Transaction Processing
- Merchant Management → [provides fees] → Transaction Processing  
- Transaction Processing → [updates] → User Dues
- Transaction Processing → [updates] → Merchant Fees
- Reporting → [reads from] → All Entities
- Frontend → [calls] → All API Endpoints

Connections:
- User.credit_limit ↔ Transaction.validation
- Merchant.fee_percentage ↔ Transaction.fee_calculation
- Transaction.history ↔ Report.generation
- API.responses ↔ Frontend.state_updates

Critical Paths:
1. User Creation → Transaction → Credit Check → Success/Failure
2. Merchant Update → Fee Change → New Transaction → Updated Calculation
3. Payback → Dues Update → Credit Availability → New Transactions

Design the system ensuring all graph connections are properly handled with:
- Data consistency across nodes
- Proper error propagation
- Transaction atomicity
- Real-time updates
```

### 2: Data Flow Graph
```YAML
Model data flow as a directed graph:

Input Nodes:
- POST /users → User Creation
- POST /merchants → Merchant Creation  
- POST /transactions → Transaction Processing
- POST /paybacks → Payment Processing

Processing Nodes:
- Validation Layer
- Business Logic Layer
- Database Layer
- Response Formatting

Output Nodes:
- API Responses
- Database Updates
- Frontend State Updates
- Report Generation

Flow Paths:
1. Request → Validation → Business Logic → Database → Response
2. Database Change → Event → Report Update → Frontend Refresh
3. Error → Error Handler → Formatted Response → Frontend Display

Implement this graph ensuring:
- Proper data validation at each node
- Error handling at every transition
- Logging for debugging
- Performance monitoring
```

### 3: Component Dependency Graph
```YAML
Map React component dependencies as a graph:

Root Components:
- App → Router → Layout

Page Components:
- UserManagement → [UserList, UserForm, UserDetails]
- MerchantManagement → [MerchantList, MerchantForm, MerchantDetails]
- TransactionDashboard → [TransactionForm, TransactionHistory]
- Reports → [DuesReport, FeeReport, CreditLimitReport]

Shared Components:
- UI Components → [Button, Input, Table, Modal]
- Service Components → [ApiClient, ErrorBoundary]
- Hook Components → [useApi, useLocalStorage, useAuth]

Dependencies:
- All pages depend on Layout
- Forms depend on UI components
- Lists depend on API hooks
- Reports depend on data formatting utils

Build the component graph ensuring:
- Minimal circular dependencies
- Clear data flow direction
- Reusable component design
- Proper prop interfaces
```

## 5. ReAct (Reasoning + Acting) Prompts

### 1: Transaction Processing ReAct
```YAML
Implement transaction processing using ReAct pattern:

Thought: I need to process a transaction between user1 and merchant2 for $400
Action: Check if user1 exists in database
Observation: User1 found with credit_limit=1000, current_dues=200

Thought: User has $200 dues, new transaction is $400, total would be $600, which is within $1000 limit
Action: Check if merchant2 exists and get fee percentage
Observation: Merchant2 found with fee_percentage=1.5%

Thought: Fee calculation: $400 * 1.5% = $6, merchant gets $394
Action: Create transaction record and update user dues
Observation: Transaction created successfully, user dues updated to $600

Thought: Need to update merchant's total collected fees
Action: Add $6 to merchant2's total_fee_collected
Observation: Merchant fees updated successfully

Final Action: Return success response
Result: {"status": "success"}

Implement this ReAct pattern in your FastAPI endpoint with proper logging of each thought and action.
```

### 2: Report Generation ReAct
```YAML
Generate user dues report using ReAct pattern:

Thought: Need to calculate total dues for all users
Action: Query all transactions from database
Observation: Found 150 transactions across 25 users

Thought: Should group transactions by user and sum amounts
Action: Aggregate transactions by user_name, sum amounts, subtract paybacks
Observation: Aggregation complete, got dues for 18 users (7 users have zero dues)

Thought: Need to identify users at credit limit
Action: Compare each user's dues with their credit_limit
Observation: Found 3 users at or above credit limit

Thought: Format response according to API specification
Action: Create response object with total and user details
Observation: Response formatted: {"total": 4250, "details": {...}}

Final Action: Return formatted report
Result: Complete dues report with user breakdown

Build this ReAct pattern into your reporting endpoints with step-by-step logging.
```

### 3: Frontend User Flow ReAct
```YAML
Handle user transaction creation using ReAct pattern:

Thought: User wants to create a transaction, need to validate form data
Action: Check if all required fields (user, merchant, amount) are filled
Observation: All fields valid, amount is positive number

Thought: Should validate if user and merchant exist before submitting
Action: Call API to verify user and merchant existence
Observation: Both user and merchant exist, can proceed

Thought: Need to show loading state while processing transaction
Action: Set loading state, disable form, call transaction API
Observation: API call in progress, user sees loading spinner

Thought: API returned success, should update UI and show confirmation
Action: Clear form, show success message, refresh transaction list
Observation: User sees success feedback, form is ready for next transaction

Alternative Path:
Thought: API returned credit limit error, should show user-friendly message
Action: Display error message, highlight amount field, suggest payback
Observation: User understands the issue and can take corrective action

Implement this ReAct pattern in your React components with proper state management.
```

## 6. Progressive Disclosure Prompts

### 1: Incremental API Development
```YAML
Build the Pay-Later API incrementally:

Level 1: Basic CRUD Operations
- Implement user creation with basic validation
- Implement merchant creation with fee validation
- Add simple health check endpoint

Level 2: Business Logic Layer
- Add transaction processing with credit limit checks
- Implement fee calculation logic
- Add payback processing

Level 3: Advanced Features
- Add comprehensive reporting endpoints
- Implement audit logging
- Add data export capabilities

For each level, provide:
- Complete working code
- Unit tests
- API documentation
- Error handling

Start with Level 1 and ensure it's fully functional before moving to Level 2.
```

### 2: Frontend Development Phases
```YAML
Build the React frontend in progressive phases:

Phase 1: Basic UI Structure
- Create layout with navigation
- Implement user management pages (list, create)
- Add basic styling with CSS/styled-components

Phase 2: Enhanced Functionality
- Add merchant management with fee updates
- Implement transaction creation form
- Add basic error handling and validation

Phase 3: Advanced Features
- Build comprehensive reporting dashboard
- Add real-time updates
- Implement advanced filtering and search

For each phase:
- Provide complete component code
- Include proper TypeScript types
- Add responsive design considerations
- Include accessibility features

Complete Phase 1 fully before proceeding to Phase 2.
```

### 3: Database Schema Evolution
```YAML
Evolve the MongoDB schema progressively:

Version 1.0: Basic Collections
- Users collection with essential fields
- Merchants collection with fee tracking
- Transactions collection for basic recording

Version 1.1: Performance Optimization
- Add indexes for common queries
- Denormalize frequently accessed data
- Add compound indexes for reporting

Version 1.2: Advanced Features
- Add audit trail fields
- Implement soft deletes
- Add data archiving strategy

For each version:
- Provide migration scripts
- Include performance benchmarks
- Add data validation rules
- Document schema changes

Implement Version 1.0 completely before enhancing to 1.1.
```

## 7. Constraint-Based Prompts

### 1: Performance Constraints
```YAML
Build the Pay-Later system with these performance constraints:
- API response time < 100ms for all endpoints
- Support 1000 concurrent users
- Database queries must use indexes
- Memory usage < 512MB per service

Given these constraints:
1. Design efficient MongoDB queries with proper indexing
2. Implement caching strategy for frequently accessed data
3. Use connection pooling for database connections
4. Add performance monitoring and alerting

Show how each constraint influences your design decisions and implementation.
```

### 2: Security Constraints
```YAML
Implement the system with these security requirements:
- All API endpoints require authentication
- Input validation on all user data
- Rate limiting: 100 requests/minute per user
- Data encryption at rest and in transit
- PCI compliance for payment data

Apply these constraints to:
1. FastAPI middleware implementation
2. Database connection security
3. Frontend authentication flow
4. Error message sanitization

Demonstrate how security constraints shape your architecture.
```

### 3: Scalability Constraints
```YAML
Implement the system with these scalability requirements:
Design for these scalability constraints:
- Horizontal scaling capability
- Database read/write separation
- Stateless service design
- Event-driven architecture readiness

Under these constraints, implement:
1. Service layer abstraction
2. Database abstraction with repository pattern
3. Configuration management for multiple environments
4. Health checks and monitoring endpoints

Show how scalability constraints influence your code structure.
```

## 8. Scenario-Based Prompts

### 1: Edge Case Scenarios
```YAML
Handle these edge case scenarios in your Pay-Later system:

Scenario 1: Concurrent Transactions
- User1 has $100 credit remaining
- Two transactions of $80 each submitted simultaneously
- Only one should succeed

Scenario 2: Merchant Fee Change Mid-Transaction
- Transaction starts with 2% fee
- Merchant changes fee to 3% during processing
- System should use original fee for in-flight transaction

Scenario 3: Database Connection Loss
- Transaction partially processed
- Database connection lost before completion
- System should rollback or retry appropriately

For each scenario, provide:
- Problem analysis
- Solution approach
- Implementation code
- Test cases
```

### 2: User Journey Scenarios
```YAML
Design the frontend for these user journey scenarios:

Journey 1: New User Onboarding
- User signs up with email
- Sets initial credit limit
- Makes first transaction
- Views their dashboard

Journey 2: Merchant Management
- Merchant logs in
- Reviews fee collection reports
- Updates fee percentage
- Monitors transaction volume

Journey 3: Payment Recovery
- User exceeds credit limit
- Gets transaction rejected
- Makes partial payback
- Retries transaction successfully

Implement complete React flows for each journey with proper state management and error handling.
```

### 3: Integration Scenarios
```YAML
Design integration scenarios for the Pay-Later system:

Scenario 1: E-commerce Platform Integration
- External store sends transaction requests
- Real-time approval/rejection responses
- Webhook notifications for payment status
- Bulk transaction processing

Scenario 2: Bank Integration
- Real-time credit limit checks
- Automated payback processing
- Transaction verification
- Fraud detection integration

Scenario 3: Mobile App Integration
- RESTful API consumption
- Push notifications
- Offline transaction queuing
- Biometric authentication

Provide API design and implementation for each integration scenario.
```

## 9. Metamorphic Prompts

### 1: Architecture Transformation
```YAML
Transform the Pay-Later monolith into microservices:

Original Form: Single FastAPI application
- All endpoints in one service
- Shared database models
- Coupled business logic

Transformed Form: Microservices architecture
- User service (authentication, profile management)
- Merchant service (merchant onboarding, fee management)
- Transaction service (payment processing, credit checks)
- Reporting service (analytics, dashboard data)

Transformation Rules:
- Maintain API contract compatibility
- Preserve data consistency
- Add service discovery
- Implement circuit breakers

Show the step-by-step transformation with proper service boundaries and communication patterns.
```

### 2: Data Model Evolution
```YAML
Evolve the data model from simple to event-sourced:

Current Form: Direct state storage
- User document with current_dues field
- Transaction documents with final state
- Simple CRUD operations

Evolved Form: Event sourcing pattern
- Events: UserCreated, TransactionProcessed, PaymentMade
- Event store for complete audit trail
- Projections for current state queries
- Event replay capabilities

Evolution Process:
- Identify all state-changing events
- Design event schemas
- Build event store and projections
- Migrate existing data to events

Implement the event-sourced version while maintaining API compatibility.
```

### 3: Frontend Architecture Evolution
```YAML
Transform the frontend from basic to advanced architecture:

Initial State: Simple React components
- Direct API calls in components
- Local component state
- Basic error handling

Advanced State: Sophisticated architecture
- Redux/Zustand for state management
- React Query for server state
- Component composition patterns
- Advanced error boundaries

Transformation Steps:
- Extract API logic to custom hooks
- Implement global state management
- Add caching and optimistic updates
- Create reusable component library

Show the progressive transformation with proper migration strategies.
```

## 10. Analogical Reasoning Prompts

### 1: Banking System Analogy
```YAML
Build the Pay-Later system like a traditional banking system:

Bank Account ↔ User Credit Account
- Account opening ↔ User onboarding
- Credit limit ↔ Overdraft facility
- Transaction ↔ Payment authorization
- Statement ↔ Dues report

Apply banking principles:
- Double-entry bookkeeping for transactions
- Audit trails for all operations
- Reconciliation processes
- Regulatory compliance patterns

Implement the system using banking industry best practices for data integrity and audit requirements.
```

### 2: Library System Analogy
```YAML
Design the system like a library management system:

Books ↔ Credit Capacity
- Book checkout ↔ Transaction processing
- Due date ↔ Payment due date
- Overdue fines ↔ Interest charges
- Return process ↔ Payback processing

Library Concepts to Apply:
- Reservation system for credit allocation
- Renewal process for extended payment terms
- Catalog system for merchant and user management
- Inventory tracking for credit availability

Build the credit management features using library system patterns.
```

### 3: Restaurant Management Analogy
```YAML
Structure the system like restaurant operations:

Menu ↔ Merchant Catalog
- Order taking ↔ Transaction creation
- Kitchen processing ↔ Payment processing
- Bill generation ↔ Dues calculation
- Payment collection ↔ Payback processing

Restaurant Workflow to Implement:
- Order validation (credit check)
- Kitchen queue (transaction queue)
- Service tracking (payment status)
- Daily reconciliation (reporting)

Apply restaurant efficiency patterns to optimize transaction processing.
```

## 11. Compositional Prompts

### 1: Modular API Design
```YAML
Compose the Pay-Later API from reusable modules:

Base Module: Common functionality
- Database connection management
- Request/response validation
- Error handling middleware
- Logging and monitoring

User Module: User-specific operations
- User CRUD operations
- Credit limit management
- Dues calculation
- Authentication/authorization

Merchant Module: Merchant-specific operations
- Merchant CRUD operations
- Fee management
- Revenue reporting
- Merchant analytics

Transaction Module: Transaction processing
- Payment processing
- Credit validation
- Fee calculation
- Transaction history

Compose these modules into a cohesive API with proper dependency injection and clean interfaces.
```

### 2: Component Composition
```YAML
Build React UI through component composition:

Atomic Components:
- Button, Input, Label, Text
- Card, Modal, Dropdown, DatePicker

Molecular Components:
- FormField (Label + Input + Error)
- DataTable (Headers + Rows + Pagination)
- StatusBadge (Icon + Text + Color)

Organism Components:
- UserForm (FormFields + Validation + Submit)
- TransactionList (DataTable + Filters + Actions)
- ReportDashboard (Charts + Metrics + Export)

Page Templates:
- DashboardLayout (Header + Sidebar + Content)
- FormLayout (Breadcrumb + Form + Actions)
- ReportLayout (Filters + Content + Export)

Compose these layers to build the complete user interface with proper prop interfaces and TypeScript types.
```

### 3: Database Layer Composition
```YAML
Compose the database layer from reusable patterns:

Base Repository Pattern:
- Generic CRUD operations
- Query building utilities
- Connection management
- Error handling

Specific Repositories:
- UserRepository extends BaseRepository
- MerchantRepository extends BaseRepository
- TransactionRepository extends BaseRepository

Business Logic Services:
- PaymentService (uses UserRepo + TransactionRepo)
- ReportingService (uses all repositories)
- ValidationService (cross-entity validation)

Database Utilities:
- Migration runner
- Index management
- Backup utilities
- Performance monitoring

Compose these layers with proper abstraction and dependency injection for a maintainable database layer.
```

## 12. Constraint Satisfaction Prompts

### 1: Multi-Constraint Optimization
```YAML
Satisfy these competing constraints in the Pay-Later system:

Constraint 1: Response time < 100ms
Constraint 2: Data consistency (ACID properties)
Constraint 3: Scalability to 10k users
Constraint 4: Cost optimization (minimal infrastructure)

Optimization Problem:
- Fast responses vs. data consistency
- Scalability vs. cost
- Features vs. performance

Solution Approach:
- Use read replicas for reports (satisfies #1, #3)
- Implement caching with TTL (satisfies #1, #4)
- Use database transactions for critical operations (satisfies #2)
- Horizontal scaling with load balancing (satisfies #3)

Implement the system architecture that best satisfies all constraints with acceptable trade-offs.
```

### 2: Resource Constraint Programming
```YAML
Design the system under these resource constraints:

Memory: 1GB total across all services
CPU: 2 cores maximum
Database: 100MB storage limit
Network: 1Mbps bandwidth

Constraint Satisfaction Strategy:
- Optimize database queries to minimize memory usage
- Implement efficient caching to reduce database load
- Use compression for API responses
- Batch database operations to reduce connection overhead

Show how each constraint influences your implementation choices and provide code that operates within these limits.
```

### 3: Business Rule Constraints
```YAML
Implement the system satisfying these business rule constraints:

Rule 1: User credit limit cannot exceed $10,000
Rule 2: Merchant fees must be between 0.1% and 10%
Rule 3: Transactions must be processed within 30 seconds
Rule 4: User dues cannot be negative
Rule 5: All financial data must be accurate to 2 decimal places

Constraint Implementation:
- Input validation for all limits
- Database constraints for data integrity
- Business logic validation before processing
- Automated testing for all constraint scenarios

Build the validation layer that enforces all business rules consistently across the system.
```

## 13. Adversarial Prompts

### 1: Security Attack Scenarios
```YAML
Design the Pay-Later system to resist these attack scenarios:

Attack 1: SQL Injection via user input
- Malicious input in user names
- Crafted transaction amounts
- API parameter manipulation

Attack 2: Race Condition Exploitation
- Concurrent credit limit bypass attempts
- Simultaneous payback and transaction
- Merchant fee manipulation during transaction

Attack 3: Input Validation Bypass
- Negative transaction amounts
- Extremely large credit limits
- Invalid email formats

Defense Implementation:
- Parameterized queries and input sanitization
- Database-level constraints and transactions
- Comprehensive input validation
- Rate limiting and monitoring

Build robust defenses against each attack vector with proper testing.
```

### 2: Data Integrity Challenges
```YAML
Protect against these data integrity threats:

Threat 1: Incomplete transaction processing
- System crash during payment processing
- Network timeout during database updates
- Partial rollback scenarios

Threat 2: Concurrent data modification
- Multiple updates to user credit limit
- Simultaneous merchant fee changes
- Race conditions in dues calculation

Threat 3: Data corruption scenarios
- Invalid transaction states
- Inconsistent user dues
- Merchant fee calculation errors

Protection Strategy:
- Implement database transactions with proper isolation
- Use optimistic locking for concurrent updates
- Add data validation at multiple layers
- Implement audit trails for change tracking

Show how to build a system that maintains data integrity under all conditions.
```

### 3: Performance Attack Scenarios
```YAML
Design defenses against performance attacks:

Attack 1: Resource exhaustion
- Large number of concurrent requests
- Memory-intensive operations
- Database connection pool exhaustion

Attack 2: Algorithmic complexity attacks
- Queries that cause full table scans
- Deeply nested JSON payloads
- Complex report generation requests

Attack 3: Cascade failure scenarios
- Database overload causing API timeouts
- Memory leaks in long-running processes
- Unhandled error scenarios

Defense Mechanisms:
- Implement rate limiting and request throttling
- Add circuit breakers for external dependencies
- Use connection pooling and resource limits
- Monitor performance metrics and set alerts

Build a resilient system that performs well under attack conditions.
```

## 14. Causal Reasoning Prompts

### 1: Root Cause Analysis Framework
```YAML
Build diagnostic capabilities into the Pay-Later system:

Symptom: Transaction failures increasing
Possible Causes:
1. Database connection issues → Check connection pool metrics
2. Credit limit validation errors → Analyze user data quality
3. Merchant service unavailability → Monitor external dependencies
4. Network timeouts → Review API response times

Causal Chain Implementation:
- Log all decision points in transaction processing
- Track timing for each processing step
- Monitor external service dependencies
- Implement health checks for all components

Diagnostic Tools:
- Real-time dashboards showing system health
- Automated alerts for anomaly detection
- Historical analysis of failure patterns
- A/B testing framework for changes

Build the monitoring and diagnostic system that helps identify root causes of issues.
```

### 2: Business Impact Analysis
```YAML
Implement causal reasoning for business decisions:

Cause: Increase merchant fee percentage
Effects:
1. Immediate: Higher revenue per transaction
2. Short-term: Possible merchant churn
3. Long-term: Market competitiveness impact

Measurement Framework:
- Track merchant retention rates
- Monitor transaction volume changes
- Analyze revenue vs. volume trade-offs
- Measure customer satisfaction metrics

Implementation:
- A/B testing for fee changes
- Gradual rollout mechanisms
- Rollback capabilities for negative impacts
- Analytics dashboard for business metrics

Build the system to support data-driven business decisions with proper cause-effect tracking.
```

### 3: Technical Debt Causality
```YAML
Analyze and address technical debt causality:

Causes of Technical Debt:
1. Rapid feature development → Code quality shortcuts
2. Changing requirements → Architecture mismatches
3. Team scaling → Knowledge gaps
4. Time pressure → Testing shortcuts

Effects of Technical Debt:
1. Slower development velocity
2. Higher bug rates
3. Increased maintenance costs
4. Developer frustration

Mitigation Strategy:
- Code quality gates in CI/CD
- Regular refactoring sprints
- Comprehensive testing strategy
- Documentation and knowledge sharing

Implement technical debt tracking and prevention mechanisms in your development process.
```

## 15. Meta-Learning Prompts

### 1: Self-Improving System Design
```YAML
Design the Pay-Later system to learn and improve over time:

Learning Dimensions:
1. Performance optimization based on usage patterns
2. Error prediction based on historical data
3. User behavior analysis for feature development
4. Resource allocation optimization

Implementation Strategy:
- Collect metrics on all system operations
- Implement machine learning models for prediction
- A/B testing framework for continuous improvement
- Feedback loops for system optimization

Self-Improvement Mechanisms:
- Automatic query optimization based on patterns
- Dynamic resource allocation
- Predictive scaling based on usage trends
- Automated error recovery strategies

Build the foundation for a system that gets better with usage and data.
```

### 2: Adaptive Architecture Patterns
```YAML
Create an architecture that adapts to changing requirements:

Adaptation Triggers:
1. Load patterns → Scale resources dynamically
2. Error rates → Switch to backup strategies
3. Feature usage → Optimize popular paths
4. Data growth → Partition and archive strategies

Adaptive Mechanisms:
- Configuration-driven feature flags
- Dynamic service discovery
- Auto-scaling based on metrics
- Circuit breakers with automatic recovery

Learning Framework:
- Continuous monitoring and analysis
- Automated experimentation platform
- Machine learning for pattern recognition
- Feedback-driven optimization

Implement an architecture that can evolve and adapt without manual intervention.
```

### 3: Knowledge Extraction System
```YAML
Build capabilities to extract and apply learnings:

Knowledge Sources:
1. System logs and metrics
2. User interaction patterns
3. Error and recovery scenarios
4. Performance bottlenecks

Learning Processes:
- Pattern recognition in system behavior
- Anomaly detection for early warning
- Optimization recommendations
- Best practice extraction

Application Mechanisms:
- Automated recommendations for improvements
- Documentation generation from patterns
- Training data for new team members
- Continuous integration of learnings

Create a system that captures, analyzes, and applies organizational learning automatically.
```
