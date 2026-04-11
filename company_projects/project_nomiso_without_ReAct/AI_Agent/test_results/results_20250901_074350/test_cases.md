# User Story Test Cases

**User Story:**
As a customer, I want to add products to a shopping cart so that I can collect multiple items before making a purchase decision.

**Analysis:**
The customer wants a convenient way to gather multiple items before committing to a purchase.  This allows them to compare options and finalize their order efficiently.

**Key Requirements:**

* Ability to add products to a shopping cart.
*  Persistence of the shopping cart contents (items remain in the cart until checked out or removed).
*  Mechanism to view the contents of the shopping cart.


**Acceptance Criteria:**
Users can add products to their cart with specified quantities.Users can view all items in their cart with total price calculation.Users can remove items from their cart or update quantities.Cart persists across user sessions until checkout or manual clearing.System prevents adding out-of-stock products to cart.System calculates subtotal, taxes, and shipping costs

# Test Cases Generated

**Generated on:** 2025-09-01 07:44:26

**Total Test Cases:** 7

## Test Cases Table

| **Test Case ID** | **Test Scenario** | **Test Steps** | **Expected Result** | **Type** | **Status** |
|---|---|---|---|---|---|
| TC001 | Authenticated user successfully adds a product to the shopping cart | 1. Register a new user via POST /register with unique username and email.
2. Log... | HTTP 201 Created response with cart item details; cart count increments by one. | Happy | Pending |
| TC002 | User views shopping cart contents after adding multiple items | 1. Repeat steps from the previous test to add two distinct products.
2. Send GET... | HTTP 200 OK response containing an array of cart items, each with product detail... | Happy | Pending |
| TC003 | Unauthenticated request to add a product to the cart is rejected | 1. Create a product via POST /products without providing an Authorization header... | HTTP 401 Unauthorized response indicating that authentication credentials are mi... | Negative | Pending |
| TC004 | Adding a non-existent product ID to the cart returns an error | 1. Register and log in as a user to obtain a JWT token.
2. Send POST /cart/items... | HTTP 404 Not Found response stating that the product does not exist. | Negative | Pending |
| TC005 | Adding the same product multiple times aggregates quantity in the cart | 1. Register, log in, and create a product.
2. Add the product to the cart twice ... | Cart contains a single entry for the product with quantity equal to the sum of a... | Edge | Pending |
| TC006 | Shopping cart persists across user sessions until checkout or removal | 1. Register and log in, then add a product to the cart.
2. Log out by discarding... | Cart still contains the previously added item(s) with correct quantities, demons... | Edge | Pending |
| TC007 | Attempting to remove a non-existent cart item returns an error | 1. Register and log in.
2. Attempt to delete cart item with DELETE /cart/items/9... | HTTP 404 Not Found response indicating that the cart item does not exist. | Negative | Pending |

## Detailed Test Cases

### TC001: Authenticated user successfully adds a product to the shopping cart

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Register a new user via POST /register with unique username and email.
2. Log in via POST /login to receive a JWT access token.
3. Create a product via POST /products using the obtained token.
4. Add the created product to the cart by sending POST /cart/items with body {"product_id": <created_product_id>, "quantity": 1} and Authorization header containing the bearer token.

**Expected Result:**
HTTP 201 Created response with cart item details; cart count increments by one.

---

### TC002: User views shopping cart contents after adding multiple items

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Repeat steps from the previous test to add two distinct products.
2. Send GET /cart with Authorization header containing the bearer token.

**Expected Result:**
HTTP 200 OK response containing an array of cart items, each with product details and quantity matching the additions.

---

### TC003: Unauthenticated request to add a product to the cart is rejected

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Create a product via POST /products without providing an Authorization header.
2. Attempt to add the product to the cart with POST /cart/items using the same unauthenticated session.

**Expected Result:**
HTTP 401 Unauthorized response indicating that authentication credentials are missing or invalid.

---

### TC004: Adding a non-existent product ID to the cart returns an error

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Register and log in as a user to obtain a JWT token.
2. Send POST /cart/items with body {"product_id": 9999, "quantity": 1} and Authorization header containing the bearer token.

**Expected Result:**
HTTP 404 Not Found response stating that the product does not exist.

---

### TC005: Adding the same product multiple times aggregates quantity in the cart

**Type:** Edge

**Status:** Pending

**Test Steps:**
1. Register, log in, and create a product.
2. Add the product to the cart twice with POST /cart/items each time.
3. Retrieve the cart via GET /cart.

**Expected Result:**
Cart contains a single entry for the product with quantity equal to the sum of additions (e.g., 2).

---

### TC006: Shopping cart persists across user sessions until checkout or removal

**Type:** Edge

**Status:** Pending

**Test Steps:**
1. Register and log in, then add a product to the cart.
2. Log out by discarding the token.
3. Log back in with the same credentials to obtain a new token.
4. Retrieve the cart via GET /cart using the new token.

**Expected Result:**
Cart still contains the previously added item(s) with correct quantities, demonstrating persistence across sessions.

---

### TC007: Attempting to remove a non-existent cart item returns an error

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Register and log in.
2. Attempt to delete cart item with DELETE /cart/items/9999 using the Authorization header.

**Expected Result:**
HTTP 404 Not Found response indicating that the cart item does not exist.

---


================================================================================

# Acceptance Criteria Validation Report

**Acceptance Criteria:**
Users can add products to their cart with specified quantities.Users can view all items in their cart with total price calculation.Users can remove items from their cart or update quantities.Cart persists across user sessions until checkout or manual clearing.System prevents adding out-of-stock products to cart.System calculates subtotal, taxes, and shipping costs

**Summary:**
- Total Test Cases: 7
- Satisfied: 6
- Not Satisfied: 1
- Satisfaction Rate: 85.7%

## ✅ Satisfied Test Cases

### Authenticated user successfully adds a product to the shopping cart
- **Steps:** 1. Register a new user via POST /register with unique username and email.
2. Log in via POST /login to receive a JWT access token.
3. Create a product via POST /products using the obtained token.
4. Add the created product to the cart by sending POST /cart/items with body {"product_id": <created_product_id>, "quantity": 1} and Authorization header containing the bearer token.
- **Expected:** HTTP 201 Created response with cart item details; cart count increments by one.

### User views shopping cart contents after adding multiple items
- **Steps:** 1. Repeat steps from the previous test to add two distinct products.
2. Send GET /cart with Authorization header containing the bearer token.
- **Expected:** HTTP 200 OK response containing an array of cart items, each with product details and quantity matching the additions.

### Adding a non-existent product ID to the cart returns an error
- **Steps:** 1. Register and log in as a user to obtain a JWT token.
2. Send POST /cart/items with body {"product_id": 9999, "quantity": 1} and Authorization header containing the bearer token.
- **Expected:** HTTP 404 Not Found response stating that the product does not exist.

### Adding the same product multiple times aggregates quantity in the cart
- **Steps:** 1. Register, log in, and create a product.
2. Add the product to the cart twice with POST /cart/items each time.
3. Retrieve the cart via GET /cart.
- **Expected:** Cart contains a single entry for the product with quantity equal to the sum of additions (e.g., 2).

### Shopping cart persists across user sessions until checkout or removal
- **Steps:** 1. Register and log in, then add a product to the cart.
2. Log out by discarding the token.
3. Log back in with the same credentials to obtain a new token.
4. Retrieve the cart via GET /cart using the new token.
- **Expected:** Cart still contains the previously added item(s) with correct quantities, demonstrating persistence across sessions.

### Attempting to remove a non-existent cart item returns an error
- **Steps:** 1. Register and log in.
2. Attempt to delete cart item with DELETE /cart/items/9999 using the Authorization header.
- **Expected:** HTTP 404 Not Found response indicating that the cart item does not exist.

## ❌ Test Cases Not Satisfying Criteria

### Unauthenticated request to add a product to the cart is rejected
- **Steps:** 1. Create a product via POST /products without providing an Authorization header.
2. Attempt to add the product to the cart with POST /cart/items using the same unauthenticated session.
- **Expected:** HTTP 401 Unauthorized response indicating that authentication credentials are missing or invalid.

