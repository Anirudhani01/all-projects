# User Story Test Cases

**User Story:**
As a customer, I want to add products to a shopping cart so that I can collect multiple items before making a purchase decision.

**Analysis:**
The user, a customer, wants a convenient way to accumulate multiple products before committing to a purchase.  This allows them to compare items and make a more informed buying decision. The main goal is to provide a shopping cart feature that supports accumulating items for later checkout.


**Key Requirements:**

* Ability to add products to a shopping cart.
* Persistence of the shopping cart contents (items remain in the cart even after navigating away from the product page).
* A visual representation of the shopping cart's contents (e.g., item list, quantity, total cost).


**Acceptance Criteria:**
Users can add products to their cart with specified quantities.Users can view all items in their cart with total price calculation.Users can remove items from their cart or update quantities.Cart persists across user sessions until checkout or manual clearing.System prevents adding out-of-stock products to cart.System calculates subtotal, taxes, and shipping costs

# Test Cases Generated

**Generated on:** 2025-09-01 07:55:22

**Total Test Cases:** 8

## Test Cases Table

| **Test Case ID** | **Test Scenario** | **Test Steps** | **Expected Result** | **Type** | **Status** |
|---|---|---|---|---|---|
| TC001 | Adding a valid product to the cart as an authenticated user | 1. Register a user. 2. Login as the registered user and obtain a JWT token. 3. G... | The product is added to the cart. A successful response (HTTP 201) is returned, ... | Happy | Pending |
| TC002 | Attempting to add a non-existent product to the cart | 1. Register a user. 2. Login and obtain a JWT token. 3. Send a POST request to /... | An error response (e.g., HTTP 404) indicating that the product was not found. | Negative | Pending |
| TC003 | Attempting to add a product to the cart without authentication | 1. Send a POST request to /cart without JWT token in the Authorization header. | An error response (HTTP 401) indicating that authentication is required. | Negative | Pending |
| TC004 | Adding multiple units of the same product to the cart | 1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. ... | The total quantity of the product in the cart should reflect the sum of all adde... | Happy | Pending |
| TC005 | Adding a product with a zero quantity to the cart | 1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. ... | The request should fail, and an appropriate error message should be returned (e.... | Negative | Pending |
| TC006 | Adding a product with a negative quantity to the cart | 1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. ... | The request should fail, and an appropriate error message should be returned (e.... | Negative | Pending |
| TC007 | Adding a product with a very large quantity to the cart (edge case) | 1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. ... | The system should handle the request appropriately. Either the product is added ... | Edge | Pending |
| TC008 | Attempting to add a product with invalid data type in the request body | 1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. ... | The system should reject the request with an appropriate error message (e.g., HT... | Negative | Pending |

## Detailed Test Cases

### TC001: Adding a valid product to the cart as an authenticated user

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Register a user. 2. Login as the registered user and obtain a JWT token. 3. Get a product ID (e.g., using GET /products). 4. Send a POST request to /cart with the product ID and quantity 1 in the request body with the JWT token in the Authorization header.

**Expected Result:**
The product is added to the cart. A successful response (HTTP 201) is returned, including the updated cart contents.

---

### TC002: Attempting to add a non-existent product to the cart

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Register a user. 2. Login and obtain a JWT token. 3. Send a POST request to /cart with a non-existent product ID.

**Expected Result:**
An error response (e.g., HTTP 404) indicating that the product was not found.

---

### TC003: Attempting to add a product to the cart without authentication

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Send a POST request to /cart without JWT token in the Authorization header.

**Expected Result:**
An error response (HTTP 401) indicating that authentication is required.

---

### TC004: Adding multiple units of the same product to the cart

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. 4. Send multiple POST requests to /cart with the same product ID and different quantities (e.g., 2, then 3).

**Expected Result:**
The total quantity of the product in the cart should reflect the sum of all added quantities.

---

### TC005: Adding a product with a zero quantity to the cart

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. 4. Send a POST request to /cart with quantity 0.

**Expected Result:**
The request should fail, and an appropriate error message should be returned (e.g., HTTP 400 Bad Request).  The product should not be added to the cart.

---

### TC006: Adding a product with a negative quantity to the cart

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. 4. Send a POST request to /cart with a negative quantity (e.g., -1).

**Expected Result:**
The request should fail, and an appropriate error message should be returned (e.g., HTTP 400 Bad Request). The product should not be added to the cart.

---

### TC007: Adding a product with a very large quantity to the cart (edge case)

**Type:** Edge

**Status:** Pending

**Test Steps:**
1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. 4. Send a POST request to /cart with an extremely large quantity (e.g., 100000).

**Expected Result:**
The system should handle the request appropriately. Either the product is added (if the system allows such large quantities) or an error is returned (e.g., HTTP 400 Bad Request) indicating that the quantity is too high.

---

### TC008: Attempting to add a product with invalid data type in the request body

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. 4. Send a POST request to /cart with the product ID as a string instead of an integer in the request body.

**Expected Result:**
The system should reject the request with an appropriate error message (e.g., HTTP 400 Bad Request) due to invalid input data type.

---


================================================================================

# Acceptance Criteria Validation Report

**Acceptance Criteria:**
Users can add products to their cart with specified quantities.Users can view all items in their cart with total price calculation.Users can remove items from their cart or update quantities.Cart persists across user sessions until checkout or manual clearing.System prevents adding out-of-stock products to cart.System calculates subtotal, taxes, and shipping costs

**Summary:**
- Total Test Cases: 8
- Satisfied: 6
- Not Satisfied: 2
- Satisfaction Rate: 75.0%

## ✅ Satisfied Test Cases

### Adding a valid product to the cart as an authenticated user
- **Steps:** 1. Register a user. 2. Login as the registered user and obtain a JWT token. 3. Get a product ID (e.g., using GET /products). 4. Send a POST request to /cart with the product ID and quantity 1 in the request body with the JWT token in the Authorization header.
- **Expected:** The product is added to the cart. A successful response (HTTP 201) is returned, including the updated cart contents.

### Adding multiple units of the same product to the cart
- **Steps:** 1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. 4. Send multiple POST requests to /cart with the same product ID and different quantities (e.g., 2, then 3).
- **Expected:** The total quantity of the product in the cart should reflect the sum of all added quantities.

### Adding a product with a zero quantity to the cart
- **Steps:** 1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. 4. Send a POST request to /cart with quantity 0.
- **Expected:** The request should fail, and an appropriate error message should be returned (e.g., HTTP 400 Bad Request).  The product should not be added to the cart.

### Adding a product with a negative quantity to the cart
- **Steps:** 1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. 4. Send a POST request to /cart with a negative quantity (e.g., -1).
- **Expected:** The request should fail, and an appropriate error message should be returned (e.g., HTTP 400 Bad Request). The product should not be added to the cart.

### Adding a product with a very large quantity to the cart (edge case)
- **Steps:** 1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. 4. Send a POST request to /cart with an extremely large quantity (e.g., 100000).
- **Expected:** The system should handle the request appropriately. Either the product is added (if the system allows such large quantities) or an error is returned (e.g., HTTP 400 Bad Request) indicating that the quantity is too high.

### Attempting to add a product with invalid data type in the request body
- **Steps:** 1. Register a user. 2. Login and obtain a JWT token. 3. Get a valid product ID. 4. Send a POST request to /cart with the product ID as a string instead of an integer in the request body.
- **Expected:** The system should reject the request with an appropriate error message (e.g., HTTP 400 Bad Request) due to invalid input data type.

## ❌ Test Cases Not Satisfying Criteria

### Attempting to add a non-existent product to the cart
- **Steps:** 1. Register a user. 2. Login and obtain a JWT token. 3. Send a POST request to /cart with a non-existent product ID.
- **Expected:** An error response (e.g., HTTP 404) indicating that the product was not found.

### Attempting to add a product to the cart without authentication
- **Steps:** 1. Send a POST request to /cart without JWT token in the Authorization header.
- **Expected:** An error response (HTTP 401) indicating that authentication is required.

