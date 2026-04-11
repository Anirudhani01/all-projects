# User Story Test Cases

**User Story:**
user want to remove a product from the cart

**Analysis:**
The user wants to easily and reliably remove items from their shopping cart, allowing them to adjust their order before checkout.  This ensures they only purchase the items they intend to buy.

**Key Requirements:**

* A mechanism to identify and select a product within the shopping cart.
* A function to remove the selected product from the cart.
* Confirmation (visual or otherwise) that the product has been successfully removed.


# Test Cases Generated

**Generated on:** 2025-08-30 19:31:13

**Total Test Cases:** 8

## Test Cases Table

| **Test Case ID** | **Test Scenario** | **Test Steps** | **Expected Result** | **Type** | **Status** |
|---|---|---|---|---|---|
| TC001 | Remove a single product from the cart - Happy Path | 1. Add a product to the cart. 2. Navigate to the cart page. 3. Click the 'Remove... | The product is removed from the cart. The cart reflects the updated quantity and... | Happy | Pending |
| TC002 | Remove multiple products from the cart - Happy Path | 1. Add multiple products to the cart (at least 2). 2. Navigate to the cart page.... | Each product is removed successfully. The cart reflects the updated quantity and... | Happy | Pending |
| TC003 | Attempt to remove a non-existent product from the cart - Negative Case | 1. Navigate to the cart page. 2. Attempt to click the 'Remove' button for a prod... | An appropriate error message is displayed, indicating that the product is not in... | Negative | Pending |
| TC004 | Attempt to remove a product from an empty cart - Negative Case | 1. Ensure the cart is empty. 2. Attempt to remove a product. | An appropriate error message is displayed, indicating that the cart is empty, or... | Negative | Pending |
| TC005 | Remove the only product in the cart - Edge Case | 1. Add one product to the cart. 2. Navigate to the cart page. 3. Click the 'Remo... | The product is removed, and the cart becomes empty.  An appropriate message (e.g... | Edge | Pending |
| TC006 | Remove a product with a quantity greater than 1 - Edge Case | 1. Add a product to the cart with a quantity greater than 1 (e.g., 3). 2. Naviga... | The quantity of the product in the cart is decremented by 1. The total price is ... | Edge | Pending |
| TC007 | Remove a product after modifying its quantity - Edge Case | 1. Add a product to the cart. 2. Modify the quantity of the product in the cart ... | The product is successfully removed from the cart after quantity modification. | Edge | Pending |
| TC008 | Attempt to remove a product after the server is down - Negative Case | 1. Add a product to the cart. 2. Simulate server downtime (e.g. stop the backend... | An appropriate error message should be displayed, indicating that the request co... | Negative | Pending |

## Detailed Test Cases

### TC001: Remove a single product from the cart - Happy Path

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Add a product to the cart. 2. Navigate to the cart page. 3. Click the 'Remove' button for the added product. 4. Observe the cart contents.

**Expected Result:**
The product is removed from the cart. The cart reflects the updated quantity and total.

---

### TC002: Remove multiple products from the cart - Happy Path

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Add multiple products to the cart (at least 2). 2. Navigate to the cart page. 3. Click the 'Remove' button for each product sequentially. 4. Observe the cart contents after each removal.

**Expected Result:**
Each product is removed successfully. The cart reflects the updated quantity and total after each removal.

---

### TC003: Attempt to remove a non-existent product from the cart - Negative Case

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Navigate to the cart page. 2. Attempt to click the 'Remove' button for a product that is not in the cart.

**Expected Result:**
An appropriate error message is displayed, indicating that the product is not in the cart, or no action is taken.

---

### TC004: Attempt to remove a product from an empty cart - Negative Case

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Ensure the cart is empty. 2. Attempt to remove a product.

**Expected Result:**
An appropriate error message is displayed, indicating that the cart is empty, or no action is taken.

---

### TC005: Remove the only product in the cart - Edge Case

**Type:** Edge

**Status:** Pending

**Test Steps:**
1. Add one product to the cart. 2. Navigate to the cart page. 3. Click the 'Remove' button for the product. 4. Observe the cart contents.

**Expected Result:**
The product is removed, and the cart becomes empty.  An appropriate message (e.g., "Your cart is empty") might be displayed.

---

### TC006: Remove a product with a quantity greater than 1 - Edge Case

**Type:** Edge

**Status:** Pending

**Test Steps:**
1. Add a product to the cart with a quantity greater than 1 (e.g., 3). 2. Navigate to the cart page. 3. Click the 'Remove' button. 4. Observe the cart contents.

**Expected Result:**
The quantity of the product in the cart is decremented by 1. The total price is adjusted accordingly.

---

### TC007: Remove a product after modifying its quantity - Edge Case

**Type:** Edge

**Status:** Pending

**Test Steps:**
1. Add a product to the cart. 2. Modify the quantity of the product in the cart (e.g., increase from 1 to 2 then decrease to 1). 3. Click 'Remove'. 4. Observe the cart.

**Expected Result:**
The product is successfully removed from the cart after quantity modification.

---

### TC008: Attempt to remove a product after the server is down - Negative Case

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Add a product to the cart. 2. Simulate server downtime (e.g. stop the backend server if possible, or use a network interruption). 3. Attempt to remove a product from the cart.

**Expected Result:**
An appropriate error message should be displayed, indicating that the request could not be completed due to server unavailability or network issues. The cart should remain unchanged.

---

