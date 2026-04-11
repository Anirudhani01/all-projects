# User Story Test Cases

**User Story:**
As a customer, I want to add products to a shopping cart so that I can collect multiple items before making a purchase decision.

**Analysis:**
The user, a customer, wants to be able to gather multiple products together before committing to a purchase.  Their goal is to easily collect a selection of items for later checkout, allowing for comparison and potential modification of their order.

Key Requirements:

*   Ability to add products to a shopping cart.
*   Persistence of the shopping cart contents (items remain in the cart until removed or checkout is initiated).
*   Mechanism to view the contents of the shopping cart.


**Acceptance Criteria:**
User can view their current profile information including username, email, and account creation date.User can update their email address while maintaining username uniqueness.User can change their password with proper validation of current password.System validates new email format and ensures it's not already in use.System requires re-authentication for sensitive profile changes.System maintains audit trail of profile modifications

# Test Cases Generated

**Generated on:** 2025-09-01 08:13:52

**Total Test Cases:** 7

## Test Cases Table

| **Test Case ID** | **Test Scenario** | **Test Steps** | **Expected Result** | **Type** | **Status** |
|---|---|---|---|---|---|
| TC001 | Authenticated user successfully adds a product to the cart | 1. Register a new user via POST /register with username, email and password.
2. ... | Response status 200 OK with a JSON payload confirming the item was added, and th... | Happy | Pending |
| TC002 | Adding the same product twice increments its quantity in the cart | 1. Follow steps 1–4 from the previous test case to add a product.
2. Repeat step... | Response status 200 OK; subsequent GET /cart/contents shows the product with qua... | Edge | Pending |
| TC003 | Unauthenticated request to add a product to the cart is rejected | 1. Register and login as in test case 1.
2. Create a product using POST /product... | Response status 401 Unauthorized with an error message indicating authentication... | Negative | Pending |
| TC004 | Adding a non‑existent product ID results in a not found error | 1. Register and login to obtain a JWT token.
2. Attempt to add a product with pr... | Response status 404 Not Found with an error message such as 'Product not found'. | Negative | Pending |
| TC005 | User can view cart contents after adding items | 1. Follow steps 1–4 from test case 1 to add a product.
2. Send GET /cart/content... | Response status 200 OK and JSON array containing an object for the added product... | Happy | Pending |
| TC006 | Cart is empty when no items have been added | 1. Register a new user and login to obtain a JWT token.
2. Send GET /cart/conten... | Response status 200 OK and an empty JSON array [] indicating the cart has no ite... | Edge | Pending |
| TC007 | Adding a product with negative quantity is rejected by validation | 1. Register, login, and create a product as in test case 1.
2. Attempt to add th... | Response status 400 Bad Request with a validation error message such as 'Quantit... | Negative | Pending |

## Detailed Test Cases

### TC001: Authenticated user successfully adds a product to the cart

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Register a new user via POST /register with username, email and password.
2. Login using POST /login with the same credentials to receive a JWT token.
3. Create a product as the authenticated seller by sending POST /products with name, description, price, category and Authorization header containing the bearer token.
4. Add the created product to the cart by POSTing to /cart/add with JSON body {"product_id": <created_product_id>, "quantity": 1} and the same Authorization header.

**Expected Result:**
Response status 200 OK with a JSON payload confirming the item was added, and the cart now contains the product with quantity 1.

---

### TC002: Adding the same product twice increments its quantity in the cart

**Type:** Edge

**Status:** Pending

**Test Steps:**
1. Follow steps 1–4 from the previous test case to add a product.
2. Repeat step 4 with the same product_id and quantity 1.

**Expected Result:**
Response status 200 OK; subsequent GET /cart/contents shows the product with quantity 2 instead of two separate entries.

---

### TC003: Unauthenticated request to add a product to the cart is rejected

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Register and login as in test case 1.
2. Create a product using POST /products with Authorization header.
3. Attempt to add the product to the cart by POSTing to /cart/add without any Authorization header.

**Expected Result:**
Response status 401 Unauthorized with an error message indicating authentication is required.

---

### TC004: Adding a non‑existent product ID results in a not found error

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Register and login to obtain a JWT token.
2. Attempt to add a product with product_id 9999 (assumed non-existent) by POSTing to /cart/add with JSON body {"product_id": 9999, "quantity": 1} and the Authorization header.

**Expected Result:**
Response status 404 Not Found with an error message such as 'Product not found'.

---

### TC005: User can view cart contents after adding items

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Follow steps 1–4 from test case 1 to add a product.
2. Send GET /cart/contents with the Authorization header.

**Expected Result:**
Response status 200 OK and JSON array containing an object for the added product, including its id, name, price, category, seller_id, and quantity 1.

---

### TC006: Cart is empty when no items have been added

**Type:** Edge

**Status:** Pending

**Test Steps:**
1. Register a new user and login to obtain a JWT token.
2. Send GET /cart/contents with the Authorization header without adding any products.

**Expected Result:**
Response status 200 OK and an empty JSON array [] indicating the cart has no items.

---

### TC007: Adding a product with negative quantity is rejected by validation

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Register, login, and create a product as in test case 1.
2. Attempt to add the product to the cart by POSTing to /cart/add with JSON body {"product_id": <created_product_id>, "quantity": -3} and the Authorization header.

**Expected Result:**
Response status 400 Bad Request with a validation error message such as 'Quantity must be greater than zero'.

---


================================================================================

# Acceptance Criteria Validation Report

**Acceptance Criteria:**
User can view their current profile information including username, email, and account creation date.User can update their email address while maintaining username uniqueness.User can change their password with proper validation of current password.System validates new email format and ensures it's not already in use.System requires re-authentication for sensitive profile changes.System maintains audit trail of profile modifications

**Summary:**
- Total Test Cases: 7
- Satisfied: 0
- Not Satisfied: 7
- Satisfaction Rate: 0.0%

## ❌ Test Cases Not Satisfying Criteria

### Authenticated user successfully adds a product to the cart
- **Steps:** 1. Register a new user via POST /register with username, email and password.
2. Login using POST /login with the same credentials to receive a JWT token.
3. Create a product as the authenticated seller by sending POST /products with name, description, price, category and Authorization header containing the bearer token.
4. Add the created product to the cart by POSTing to /cart/add with JSON body {"product_id": <created_product_id>, "quantity": 1} and the same Authorization header.
- **Expected:** Response status 200 OK with a JSON payload confirming the item was added, and the cart now contains the product with quantity 1.

### Adding the same product twice increments its quantity in the cart
- **Steps:** 1. Follow steps 1–4 from the previous test case to add a product.
2. Repeat step 4 with the same product_id and quantity 1.
- **Expected:** Response status 200 OK; subsequent GET /cart/contents shows the product with quantity 2 instead of two separate entries.

### Unauthenticated request to add a product to the cart is rejected
- **Steps:** 1. Register and login as in test case 1.
2. Create a product using POST /products with Authorization header.
3. Attempt to add the product to the cart by POSTing to /cart/add without any Authorization header.
- **Expected:** Response status 401 Unauthorized with an error message indicating authentication is required.

### Adding a non‑existent product ID results in a not found error
- **Steps:** 1. Register and login to obtain a JWT token.
2. Attempt to add a product with product_id 9999 (assumed non-existent) by POSTing to /cart/add with JSON body {"product_id": 9999, "quantity": 1} and the Authorization header.
- **Expected:** Response status 404 Not Found with an error message such as 'Product not found'.

### User can view cart contents after adding items
- **Steps:** 1. Follow steps 1–4 from test case 1 to add a product.
2. Send GET /cart/contents with the Authorization header.
- **Expected:** Response status 200 OK and JSON array containing an object for the added product, including its id, name, price, category, seller_id, and quantity 1.

### Cart is empty when no items have been added
- **Steps:** 1. Register a new user and login to obtain a JWT token.
2. Send GET /cart/contents with the Authorization header without adding any products.
- **Expected:** Response status 200 OK and an empty JSON array [] indicating the cart has no items.

### Adding a product with negative quantity is rejected by validation
- **Steps:** 1. Register, login, and create a product as in test case 1.
2. Attempt to add the product to the cart by POSTing to /cart/add with JSON body {"product_id": <created_product_id>, "quantity": -3} and the Authorization header.
- **Expected:** Response status 400 Bad Request with a validation error message such as 'Quantity must be greater than zero'.

