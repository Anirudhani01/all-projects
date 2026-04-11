Of course. Here is the previous response formatted as requested.

## 1\. Persona Prompts

### 1: Senior Full-Stack Developer

```yaml
persona: Senior Full-Stack Developer
expertise: [Python FastAPI, MongoDB (async with Motor), React, TypeScript]
principles:
  - Writes clean, scalable, and well-documented code.
  - Follows modern best practices.
  - Prioritizes efficiency, atomic operations, and clear error handling.
goal: Help me build the "PayLater" service from the ground up.
initial_task: Outline a project structure with separate directories for the backend and frontend.
```

### 2: Backend Specialist

```yaml
persona: Backend Specialist
focus: FastAPI
task: Implement the core transaction logic.
constraints:
  - Prioritize database efficiency.
  - Ensure operations are atomic where necessary.
  - Implement clear and robust error handling.
```

### 3: Frontend Specialist

```yaml
persona: Senior Frontend Engineer
expertise: [React, TypeScript, Tailwind CSS]
specialization: Building intuitive and accessible user interfaces.
task: Create a React form component for users to submit a payback.
requirements:
  - Use functional components and hooks.
  - Implement proper state management for input fields.
  - Handle form submission gracefully, including loading and error states.
```

-----

## 2\. Few-Shot Prompts

### 1: Pydantic Model Generation

````yaml
task: Generate Pydantic models for MongoDB collections.
style_guide: Follow the provided example precisely for structure, typing, and configuration.

example:
  input: A model for a User with name, email, credit limit, and dues.
  output: >
    ```python
    from pydantic import BaseModel, Field, EmailStr
    from typing import Optional
    from bson import ObjectId

    class PyObjectId(ObjectId):
        @classmethod
        def __get_validators__(cls): yield cls.validate
        @classmethod
        def validate(cls, v):
            if not ObjectId.is_valid(v): raise ValueError("Invalid objectid")
            return ObjectId(v)
        @classmethod
        def __get_pydantic_json_schema__(cls, field_schema):
            field_schema.update(type="string")

    class User(BaseModel):
        id: Optional[PyObjectId] = Field(alias="_id", default=None)
        name: str = Field(...)
        email: EmailStr = Field(...)
        credit_limit: float = Field(..., gt=0)
        dues: float = Field(default=0.0)

        class Config:
            arbitrary_types_allowed = True
            json_encoders = {ObjectId: str}
    ```

new_request:
  input: A model for a Merchant with a name and a fee percentage.
  output: # Generate here
````

### 2: FastAPI Endpoint Generation

````yaml
task: Create FastAPI endpoints.
style_guide: Use the provided example's structure, including dependency injection for the database, response models, and status codes.

example:
  input: A POST endpoint at `/users` to create a new user.
  output: >
    ```python
    from fastapi import APIRouter, Body, status, HTTPException, Depends
    from pymongo.database import Database
    # ... imports

    router = APIRouter()

    @router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
    async def create_user(user: User = Body(...), db: Database = Depends(get_db)):
        if await db["users"].find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="User with this email already exists")
        new_user = await db["users"].insert_one(user.dict(by_alias=True))
        created_user = await db["users"].find_one({"_id": new_user.inserted_id})
        return created_user
    ```

new_request:
  input: A POST endpoint at `/merchants` to create a new merchant.
  output: # Generate here
````

### 3: React Component Generation

````yaml
task: Generate simple React display components using TypeScript.
style_guide: Follow the structure of a functional component with a typed props interface.

example:
  input: A component to display user dues.
  output: >
    ```tsx
    import React from 'react';

    interface UserDuesProps {
      userName: string;
      dues: number;
    }

    const UserDues: React.FC<UserDuesProps> = ({ userName, dues }) => {
      return (
        <div className="p-4 border rounded-lg shadow-md">
          <h3 className="text-lg font-semibold">{userName}</h3>
          <p>Current Dues: <span className="font-bold text-red-500">${dues.toFixed(2)}</span></p>
        </div>
      );
    };

    export default UserDues;
    ```

new_request:
  input: A component named `MerchantFee` that takes `merchantName` and `feePercentage` as props and displays them.
  output: # Generate here
````

-----

## 3\. Chain-of-Thought (CoT) Prompts

### 1: Transaction Processing Logic

```yaml
task: Implement the logic for the `POST /transactions` endpoint.

chain_of_thought:
  - First, provide a step-by-step breakdown of the entire process.
  - Step 1: Find the user and merchant documents in MongoDB. Handle cases where they don't exist.
  - Step 2: Calculate the user's available credit (credit_limit - current_dues).
  - Step 3: Check if the transaction amount is greater than the available credit. If so, reject.
  - Step 4: If successful, create a new document in the `transactions` collection.
  - Step 5: Atomically update the `dues` field on the user's document.
  - Step 6: Define the structure for success and failure JSON responses.

implementation:
  - After detailing this plan, write the full async FastAPI endpoint function that implements it.
```

### 2: Total Dues Reporting Logic

```yaml
task: Create the `GET /reports/total-dues` endpoint.

chain_of_thought:
  - First, outline the most efficient way to get total dues from all users using MongoDB.
  - Step 1: Propose a MongoDB aggregation pipeline.
  - Step 2: The pipeline should filter out users with zero dues.
  - Step 3: It should then group all results to calculate the total sum and construct the `details` object.
  - Step 4: A final `$project` stage might be needed to format the output to `{"total": <num>, "details": {<user>: <dues>}}`.

implementation:
  - After explaining the pipeline, write the FastAPI endpoint code that executes it using `motor`.
```

### 3: Frontend Dashboard State Logic

```yaml
task: Build the main user dashboard component in React.

chain_of_thought:
  - First, think step-by-step about the required state and effects.
  - Step 1: What pieces of local state (`useState`) are needed? (e.g., `userData`, `transactions`, `loading`, `error`).
  - Step 2: Which API calls need to be made? (e.g., fetch user details, fetch transaction history).
  - Step 3: How should `useEffect` be used to trigger these fetches when the component mounts?
  - Step 4: How will the UI conditionally render based on the `loading` and `error` states?

implementation:
  - After explaining the strategy, write the complete React component code.
```

-----

## 4\. Tree of Thought (ToT) Prompts

### 1: Database Schema Design

```yaml
problem: I need to decide how to store transaction data in MongoDB for the PayLater app.

explore_approaches:
  - Approach 1 (Embedded): Store an array of transaction sub-documents directly within each `user` document.
  - Approach 2 (Referenced): Create a separate `transactions` collection and link transactions to users via a `user_id` field.

evaluate:
  - For each approach, analyze the pros and cons regarding:
    - Read performance (getting a user's transactions).
    - Write performance (adding a new transaction).
    - Scalability (what if a user has thousands of transactions?).
    - Reporting flexibility (e.g., calculating total fees from all transactions).

conclude_and_implement:
  - Based on the evaluation, recommend the best approach for this specific application.
  - Provide the Pydantic models for your chosen schema design.
```

### 2: Payback Logic Implementation

```yaml
problem: How should we implement the logic for the `POST /paybacks` endpoint?

explore_approaches:
  - Approach 1 (Simple Subtraction): Directly find the user document and decrement the `dues` field by the payback amount.
  - Approach 2 (Ledger-based): Create a new document in a `paybacks` collection for each payback. The user's `dues` would be a calculated value (sum of transactions - sum of paybacks).

evaluate:
  - Analyze the pros and cons of each method regarding:
    - Simplicity and ease of implementation.
    - Auditability and having a historical record of all paybacks.
    - Performance implications of calculating dues on the fly vs. storing a decremented value.

conclude_and_implement:
  - Choose the more robust and auditable option.
  - Write the complete FastAPI endpoint logic for your chosen approach.
```

### 3: API Versioning Strategy

```yaml
problem: As the service grows, we will need a strategy for versioning our API to avoid breaking changes.

explore_approaches:
  - Propose three different API versioning strategies:
    1. URI Path Versioning (e.g., `/api/v1/users`)
    2. Query Parameter Versioning (e.g., `/api/users?version=1`)
    3. Custom Header Versioning (e.g., `X-API-Version: 1`)

evaluate:
  - Discuss the advantages and disadvantages of each strategy in the context of a FastAPI application.
  - Consider ease of implementation, discoverability, and impact on routing.

conclude_and_implement:
  - Recommend the most suitable strategy for a new project like this.
  - Show a small code example of how to structure the FastAPI `APIRouter` for the recommended strategy.
```

-----

## 5\. Graph of Thought (GoT) Prompts

### 1: Hybrid Error Handling System

```yaml
goal: Design a robust and clean error handling system for the FastAPI backend.

idea_1:
  method: Use FastAPI's built-in `HTTPException` directly within endpoint logic.
  benefit: Simplicity and speed of implementation.

idea_2:
  method: Create custom domain-specific exception classes (e.g., `CreditLimitExceededError`).
  benefit: Clear separation of concerns and more descriptive business logic.

synthesis_task:
  - Design a hybrid approach that combines the benefits of both.
  - The business logic (service layer) should raise custom exceptions.
  - A global exception handler middleware should catch these custom exceptions and convert them into standard, user-friendly HTTP responses.

implementation:
  - Write the code for a custom `CreditLimitExceededError` exception.
  - Write the FastAPI global exception handler function.
  - Show how the transaction endpoint would use the custom exception.
```

### 2: Flexible Reporting Architecture

```yaml
goal: Design the reporting feature to be both simple to use and easy to extend.

idea_1:
  method: Create a separate, dedicated endpoint for each required report (e.g., `/reports/dues/{user_name}`).
  benefit: Explicit, easy to discover, and simple to implement.

idea_2:
  method: Create a single, generic endpoint (`/reports`) that uses query parameters to define the report to be generated.
  benefit: Flexible and avoids creating new endpoints for every new report.

synthesis_task:
  - Let's merge these ideas to avoid code duplication.
  - Keep the simple, dedicated endpoint routes as the public API.
  - Design a single, powerful *internal* service function, `generate_report(report_type, **filters)`, that contains the core logic.
  - Each dedicated endpoint will call this central function with the correct parameters.

implementation:
  - Show the function signature and a conceptual implementation of `generate_report`.
  - Show how the `GET /reports/dues/{user_name}` endpoint would use this new service function.
```

### 3: Combined React State Management

```yaml
goal: Define a clear state management strategy for the React frontend.

idea_1:
  method: Use local `useState` for component-specific state.
  benefit: Simple, built-in, and perfect for things like form inputs.

idea_2:
  method: Use a global `Context` for application-wide state.
  benefit: Avoids prop drilling for data needed by many components (e.g., logged-in user info).

synthesis_task:
  - Create a strategy that uses both techniques appropriately.
  - The transaction form component should use its own local `useState` for managing the amount and merchant inputs.
  - Create a `UserContext` that holds global user data, like total dues.
  - After a successful transaction, the form component should call a function from the context to refresh the global user data.

implementation:
  - Write the code for the `UserProvider` context.
  - Write the code for the `TransactionForm` component, showing how it uses both local state and the shared context.
```

-----

## 6\. ReAct (Reason + Act) Prompts

### 1: Building an Endpoint Iteratively

````yaml
# This is a conversational sequence.
- user: "Let's build the `POST /paybacks` endpoint. First step: create the Pydantic model for the request body. It should contain `user_name` and `amount`."
- assistant:
    thought: The user wants a Pydantic model. It needs two fields: `user_name` (string) and `amount` (float, must be positive). I'll create a class `PaybackRequest` for this.
    act: >
      ```python
      from pydantic import BaseModel, Field
      class PaybackRequest(BaseModel):
          user_name: str
          amount: float = Field(..., gt=0)
      ```
- user: "Looks good. Now scaffold the FastAPI endpoint `process_payback` that uses this model. No logic yet, just a `pass` statement."
- assistant:
    thought: The user wants the endpoint function signature. I need `@router.post("/paybacks")`, the function definition `async def process_payback`, and the request body parameter typed with our new model.
    act: >
      ```python
      @router.post("/paybacks", response_model=...)
      async def process_payback(payload: PaybackRequest = Body(...), db: Database = Depends(get_db)):
          pass
      ```
- user: "Perfect. Now, implement the user lookup logic. Raise a 404 if the user is not found."
````

### 2: Debugging a Failing Component

````yaml
# This is a conversational sequence.
- user: "My transaction form isn't working. When I click submit, the page just reloads. Here's my code: [paste broken React form code]."
- assistant:
    thought: A page reload on form submission usually means `event.preventDefault()` is missing. I'll check the `handleSubmit` function in the provided code. I also see they are not handling the promise from the API call, so there's no feedback.
    act: >
      You're missing `event.preventDefault()` at the beginning of your `handleSubmit` function. Without it, the browser performs its default form submission behavior, which is to reload the page.

      You should also handle the async API call properly with `.then()` and `.catch()` or async/await with a try/catch block to give the user feedback. Here's the corrected handler:
      ```javascript
      const handleSubmit = async (event) => {
        event.preventDefault(); // This is the fix
        // ... your API call logic with state updates
      };
      ```
````

### 3: Refactoring a Large Function

````yaml
# This is a conversational sequence.
- user: "This transaction function is over 50 lines long and hard to read. [paste long function code]. What is the first and most obvious thing we can extract into a separate helper function?"
- assistant:
    thought: The function fetches data, validates it, and then writes to the database. The validation logic is a good candidate for extraction because it's a self-contained set of checks (user exists, merchant exists, credit limit is sufficient).
    act: >
      The validation logic is the best candidate to extract first. We can create a helper function called `validate_transaction_is_possible`. It would take the user, merchant, and transaction amount, and it would raise specific exceptions if any check fails. This will make the main function read like a clear set of steps.

      Here's how the helper function could look:
      ```python
      async def validate_transaction_is_possible(user: User, merchant: Merchant, amount: float):
          if not user:
              raise HTTPException(status_code=404, detail="User not found")
          if not merchant:
              raise HTTPException(status_code=404, detail="Merchant not found")
          if (user.dues + amount) > user.credit_limit:
              raise HTTPException(status_code=400, detail="Credit limit exceeded")
      ```
- user: "Excellent. Now, rewrite the main endpoint to use this new helper."
````

-----

## 7\. Zero-Shot Prompts

### 1: Pydantic Model Creation

```yaml
Write a Pydantic model for a `Transaction`. It must include `user_name`, `merchant_name`, `amount`, and a `timestamp` with a default value of the current time.
```

### 2: Database Connection

```yaml
Write a Python function using the `motor` async driver to connect to a MongoDB database. The connection string should be read from an environment variable named `MONGO_CONNECTION_STRING`.
```

### 3: Basic React Component

```yaml
Generate a basic React functional component named `AppFooter`. It should render a `<footer>` element containing the text "© 2025 PayLater Service".
```

-----

## 8\. Step-by-Step Generation Prompts

### 1: Full API Vertical Slice

```yaml
task: Create the full vertical slice for updating a merchant's fee.
generate_in_sequence:
  - 1: First, write the Pydantic model for the `PATCH` request body. It should only contain `fee_percentage: float`.
  - 2: Next, write the database service function `update_merchant_fee(db, merchant_name, new_fee)` that performs the update in MongoDB and returns the updated document.
  - 3: Finally, write the complete FastAPI `PATCH /merchants/{merchant_name}` endpoint that uses the model and the service function.
```

### 2: React Form with Custom Hook

```yaml
task: Build the UI for adding a new merchant.
generate_in_sequence:
  - 1: First, create a custom React hook named `useAddMerchant`. It should handle the state for `isLoading`, `error`, and `data`, and expose a function to execute the POST request to `/merchants`.
  - 2: Then, create a React component named `AddMerchantForm`. It should use the `useAddMerchant` hook and render a form with inputs for `name` and `fee_percentage`, a submit button, and display loading or error states.
```

### 3: Backend Project Initialization

```yaml
task: Set up the basic file structure and dependencies for the backend.
generate_in_sequence:
  - 1: Create the content for a `requirements.txt` file containing `fastapi`, `uvicorn[standard]`, `pydantic`, `motor`, and `python-dotenv`.
  - 2: Create the content for a `main.py` file that sets up a basic FastAPI app instance with a single root endpoint that returns `{"message": "Welcome to PayLater"}`.
  - 3: Create the content for a `.env.example` file containing the line `MONGO_CONNECTION_STRING="your_mongodb_uri_here"`.
```

-----

## 9\. Test-Driven Development (TDD) Prompts

### 1: Core Logic TDD

```yaml
task: Implement the core transaction credit check logic.

step_1_write_tests:
  - Using `pytest`, write a test file for a function `can_user_transact(user_dues, credit_limit, transaction_amount)`.
  - The tests must cover these cases:
    - Case 1 (Success): A transaction that is well within the credit limit. Should return True.
    - Case 2 (Edge): A transaction that exactly meets the remaining credit limit. Should return True.
    - Case 3 (Failure): A transaction that exceeds the credit limit. Should return False.

step_2_write_implementation:
  - After providing the tests, write the Python implementation of the `can_user_transact` function that makes all the tests pass.
```

### 2: API Endpoint TDD

```yaml
task: Build the `GET /reports/dues/{user_name}` endpoint.

step_1_write_test:
  - Using FastAPI's `TestClient` and `pytest`, write a single test for this endpoint.
  - The test should:
    1. Create a mock user in a temporary database with dues of 250.50.
    2. Call the endpoint `/reports/dues/mock_user`.
    3. Assert that the HTTP status code is 200.
    4. Assert that the response JSON is `{"dues": 250.50}`.

step_2_write_implementation:
  - Now, provide the full FastAPI endpoint implementation that would make this test pass.
```

### 3: React Component TDD

```yaml
task: Build the "Users at Credit Limit" reporting component.

step_1_write_test:
  - Using React Testing Library and Vitest/Jest, write a test for a component named `UsersAtLimitList`.
  - The test should:
    1. Render the component with an array of user names as props: `['user1', 'user3', 'user8']`.
    2. Assert that the text "user1", "user3", and "user8" are all present in the document.
    3. Test the case where the props array is empty, asserting that a message like "No users are at their limit" is displayed.

step_2_write_implementation:
  - Write the React component code for `UsersAtLimitList` that passes these tests.
```

-----

## 10\. Self-Correction / Refinement Prompts

### 1: Refactor for Performance

````yaml
context:
  - Here is my current, inefficient implementation for the `/reports/users-at-credit-limit` endpoint.
  - code: >
      ```python
      @router.get("/reports/users-at-credit-limit")
      async def get_users_at_limit(db: Database = Depends(get_db)):
          users_at_limit = []
          cursor = db["users"].find({})
          async for user_doc in cursor:
              if user_doc["dues"] >= user_doc["credit_limit"]:
                  users_at_limit.append(user_doc["name"])
          return users_at_limit
      ```

task:
  - This is inefficient as it fetches all user data and loops in Python.
  - Refactor this code to use a single, efficient MongoDB query that filters and projects the data at the database level.
````

### 2: Improve React Component Structure

```yaml
context:
  - My React component for creating a transaction works, but the file is over 100 lines and mixes state management, API calls, and rendering logic.
  - code: `[Assume a large, messy React component is pasted here]`

task:
  - Please review and refactor this component.
  - Your refactoring should prioritize separation of concerns.
  - Specifically, extract the API calling logic and related states (`loading`, `error`) into a custom hook (e.g., `useCreateTransaction`).
  - The main component file should be left with only the UI and state management for the form inputs.
```

### 3: Add Robust Error Handling

````yaml
context:
  - This function for creating a merchant is too optimistic and lacks any error handling.
  - code: >
      ```python
      @router.post("/merchants")
      async def create_merchant(merchant: Merchant, db: Database = Depends(get_db)):
          await db["merchants"].insert_one(merchant.dict(by_alias=True))
          return merchant
      ```

task:
  - Please add robust error handling to this code.
  - It should check if a merchant with the same name already exists in the database. If so, it must raise an `HTTPException` with a `400` status code.
  - It should also wrap the database insertion in a `try/except` block to catch potential database errors.
````

-----

## 11\. Code Block Specification Prompts

### 1: Create a New Model File

```yaml
file_path: backend/models/transaction.py
action: create
content: >
  Create a new Pydantic model named `Transaction`. It must include the following fields:
  - `user_name`: string
  - `merchant_name`: string
  - `amount`: float
  - `fee_applied`: float
  - `timestamp`: datetime, with a Pydantic `default_factory=datetime.utcnow`
```

### 2: Add a Route to an Existing File

```yaml
file_path: backend/api/v1/endpoints/users.py
action: update
content: >
  1. Import the `User` model from `backend/models/user.py`.
  2. Add a new GET endpoint at the path `/{user_name}`.
  3. The endpoint should fetch a single user's details by their name from the database.
  4. It should return the user details using the `User` response model.
  5. Handle the case where the user is not found by raising a 404 error.
```

### 3: Modify a React App Router

```yaml
file_path: frontend/src/App.tsx
action: update
content: >
  1. Import the `AddMerchantForm` component from `./components/AddMerchantForm`.
  2. Import `Routes`, `Route` from `react-router-dom`.
  3. Wrap the main content in a `<Routes>` component.
  4. Add a new `<Route>` with the path `/merchants/new` that renders the `<AddMerchantForm />` component.
```

-----

## 12\. Golden Path / Error Handling Split Prompts

### 1: Transaction Logic Split

```yaml
# Prompt 1: Golden Path
task: >
  Write the FastAPI transaction endpoint. For now, focus only on the "happy path".
  Assume the user and merchant definitely exist and the user has unlimited credit.
  Just implement the logic for creating the transaction record in the database and updating the user's dues field.

# Prompt 2: Add Error Handling
task: >
  Now, take the golden path code from above and make it robust.
  Add the following checks at the beginning of the function:
  1. Verify the user exists. If not, raise 404.
  2. Verify the merchant exists. If not, raise 404.
  3. Add the credit limit check. If it fails, raise a 400 response with the reason "credit limit exceeded".
```

### 2: User Onboarding Form Split

```yaml
# Prompt 1: Golden Path
task: >
  Write a React form component for onboarding a new user.
  Assume the user fills out every field correctly and the API call is always successful.
  Do not include any validation or error message display logic yet.

# Prompt 2: Add Error Handling
task: >
  Now, add client-side validation and error handling to that form.
  1. The email input must be validated for a correct email format.
  2. The credit limit input must be a positive number.
  3. Show a red error message text below any invalid input field.
  4. Handle the case where the API submission fails (e.g., email already exists) by showing a general error message at the top of the form.
```

### 3: Reporting Endpoint Split

```yaml
# Prompt 1: Golden Path
task: >
  Write the reporting endpoint to calculate the total fees collected for a specific merchant.
  Just write the core MongoDB aggregation logic to sum the fees from transactions for that merchant.
  Assume the merchant name provided is always valid and exists.

# Prompt 2: Add Error Handling
task: >
  Now, add edge case handling to that endpoint.
  1. Add a check at the beginning to see if the merchant exists. If not, return a 404.
  2. If the merchant exists but has zero transactions, ensure the endpoint returns `{"fee_collected": 0.0}` instead of null or an error.
```

-----

## 13\. Context Stuffing / System Prompts

### 1: Start of Coding Session

````yaml
context:
  project: PayLater Service
  stack: [FastAPI, MongoDB, React]
  summary: I am building a PayLater application. Here is the complete context. Please read it carefully and refer to it for all subsequent requests.

  requirements_document: >
    # The full text from the user's provided PDF requirements would be pasted here.
    # Overview, Use Cases, API specs, Example Flow, etc.

  current_schema: >
    ```python
    # Paste existing Pydantic models for User and Merchant here.
    ```

  file_structure:
    - backend/main.py
    - backend/models/user.py
    - backend/api/v1/users.py

initial_task:
  - With all the context provided above, my first request is to build the `POST /transactions` endpoint.
  - Please generate the code for a new file: `backend/api/v1/transactions.py`.
````

### 2: Mid-Project Debugging

````yaml
context:
  project: PayLater Service
  task: Debugging an issue in the fee calculation logic.
  requirements: >
    - The transaction fee is calculated as `amount * (fee_percentage / 100)`.
    - The fee can be changed by the merchant at any time.
  relevant_code: >
    ```python
    # Paste the problematic function here
    async def create_transaction(...):
      # ...
      fee = amount * merchant.fee_percentage # Potential bug here?
      # ...
    ```

question:
  - The fee calculation is sometimes incorrect for historical transactions when I run reports.
  - Based on the context that a merchant's fee can change, what is the flaw in my current `create_transaction` logic?
  - How should I change my database schema and logic to correctly store the fee that was applied *at the time of the transaction*?
````

### 3: Frontend Context Loading

````yaml
context:
  project: PayLater Service Frontend
  tech_stack: [React, TypeScript, Tailwind CSS, Axios]
  conventions:
    - All API calls are managed in a central `src/apiClient.ts` file.
    - Components should be functional and use hooks.
  api_client_setup: >
    ```typescript
    // src/apiClient.ts
    import axios from 'axios';
    export const apiClient = axios.create({ baseURL: '/api/v1' });
    ```
  sample_component: >
    ```tsx
    // Example of a typical display component
    // src/components/UserInfo.tsx
    // ...
    ```

initial_task:
  - Now, let's build the user dashboard component.
  - It should be located at `src/pages/Dashboard.tsx`.
  - It needs to use our `apiClient` to fetch data from `/users/{username}` and `/transactions/user/{username}`.
````

-----

## 14\. Instruction Templating Prompts

### 1: API Endpoint Template

````yaml
task: Generate a new API endpoint using my defined template.

template: >
  ```python
  @router.<METHOD>("/<PATH>", response_model=<RESPONSE_MODEL>, status_code=<STATUS_CODE>)
  async def <FUNCTION_NAME>(<PARAMS>, db: Database = Depends(get_db)):
      # 1. Fetch required documents from DB.
      # 2. Perform business logic/validation.
      # 3. Update/create documents in DB.
      # 4. Return the response.
````

fill\_values:
METHOD: POST
PATH: "/paybacks"
RESPONSE\_MODEL: PaybackResponse \# You can define this model
STATUS\_CODE: status.HTTP\_200\_OK
FUNCTION\_NAME: create\_payback
PARAMS: payload: PaybackRequest = Body(...)
LOGIC:
\- Fetch the user by `payload.user_name`.
\- Decrease the user's `dues` by `payload.amount`. Do not let dues go below zero.
\- Save the user document.
\- Return the user's name and their `remaining_dues`.

````

### 2: React Form Component Template
```YAML
task: Create the `UpdateMerchantFeeForm` component using my form template.

template: >
  ```tsx
  import React, { useState } from 'react';

  // Define Props Interface here
  interface <FORM_NAME>Props { ... }

  const <FORM_NAME>: React.FC<<FORM_NAME>Props> = (props) => {
    // 1. Setup useState for form fields
    const [field1, setField1] = useState('');

    // 2. Handle form submission
    const handleSubmit = (e) => { ... };

    // 3. Render the JSX form
    return (
      <form onSubmit={handleSubmit}>
        {/* Form content goes here */}
      </form>
    );
  }
````

fill\_values:
FORM\_NAME: UpdateMerchantFeeForm
PROPS: It should take a `merchantName` prop.
STATE: One state variable for the new `feePercentage`.
SUBMIT\_LOGIC: On submit, it should make a PATCH request to `/merchants/{merchantName}`.
JSX: A single number input for the fee percentage and a submit button.

````

### 3: Database Service Function Template
```YAML
task: Create a database service function using my template.

template: >
  ```python
  from pymongo.database import Database

  async def <ACTION>_<DOCUMENT>(db: Database, identifier: str, data: dict = None):
    """
    <DOCSTRING>
    """
    # Implementation here
````

fill\_values:
ACTION: find\_and\_update
DOCUMENT: user
DOCSTRING: Finds a user by email and updates their document with the provided data.
IMPLEMENTATION:
\- Use `db["users"].find_one_and_update`.
\- The first parameter should be a filter for `{"email": identifier}`.
\- The second parameter should be the update document using the `$set` operator with `data`.
\- It should return the updated user document.

````
***
## 15. Metacognitive Prompts

### 1: Reviewing Transaction Logic for Race Conditions
```YAML
context:
  - You previously generated this code for handling transactions.
  - code: >
      ```python
      # Assume code that does a separate read then write:
      # 1. user = find_user(...)
      # 2. if user.dues + amount <= user.credit_limit:
      # 3.    update_user_dues(...)
      ```
metacognitive_questions:
  - Thank you. Before I proceed, please analyze this logic.
  - 1. What race conditions could occur here if two transaction requests for the same user arrive at nearly the same time?
  - 2. How could this lead to the user's credit limit being exceeded?
  - 3. How would you modify the code to use an atomic database operation (like MongoDB's `find_one_and_update` with a query filter) to prevent this race condition entirely? Please provide the updated, safer code.
````

### 2: Questioning React Hook Dependencies

````yaml
context:
  - Here is a custom data fetching hook you wrote for me.
  - code: >
      ```tsx
      const useUserData = (userId) => {
        const [user, setUser] = useState(null);
        useEffect(() => {
          apiClient.get(`/users/${userId}`).then(res => setUser(res.data));
        }, []); // <-- Note the empty dependency array
      }
      ```
metacognitive_questions:
  - Please review this React hook you wrote.
  - 1. You've used an empty dependency array `[]` in the `useEffect` hook. What is the potential bug this creates if the `userId` prop changes after the component has mounted?
  - 2. What is the correct dependency array to fix this bug?
  - 3. Are there any other issues, such as a missing cleanup function to handle unmounted components?
````

### 3: Final Security and Edge Case Review

```yaml
context:
  - You've helped me generate the complete backend service for the PayLater app.
  - The code for all endpoints (`/users`, `/merchants`, `/transactions`, etc.) is now complete.

metacognitive_questions:
  - Before we finalize, please perform a high-level review of the entire application concept you've helped build.
  - 1. What is the single biggest security vulnerability in this application as we've designed it? (Consider aspects like authentication, authorization, input validation). How would you recommend we fix it?
  - 2. What are two critical edge cases the current logic might not handle? (e.g., What happens if a user's credit limit is updated to be lower than their current dues? What about negative payback amounts?)
  - 3. Could the reporting endpoints become a performance bottleneck? If so, what strategy (e.g., indexing, caching) should be implemented first?
```