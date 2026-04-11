# User Story Test Cases

**User Story:**
As a registered user, I want to view and update my profile information so that I can keep my account details current and accurate.

**Analysis:**
The user wants to maintain accurate and up-to-date personal information associated with their account.  This allows them to ensure their account reflects their current details and facilitates a positive user experience.  The core goal is self-service management of user profile data.

Key Requirements:

* **View Profile Information:**  Ability to see existing profile data.
* **Update Profile Information:** Ability to modify existing profile data (e.g., name, address, email, phone number).  This should include appropriate validation to ensure data accuracy (e.g., email format).
* **Authentication:** The user must be authenticated (logged in) to access this functionality.


**Acceptance Criteria:**
User can view their current profile information including username, email, and account creation date.User can update their email address while maintaining username uniqueness.User can change their password with proper validation of current password.System validates new email format and ensures it's not already in use.System requires re-authentication for sensitive profile changes.System maintains audit trail of profile modifications

# Test Cases Generated

**Generated on:** 2025-08-31 14:33:39

**Total Test Cases:** 8

## Test Cases Table

| **Test Case ID** | **Test Scenario** | **Test Steps** | **Expected Result** | **Type** | **Status** |
|---|---|---|---|---|---|
| TC001 | Successfully view user profile information after successful login | 1. Send a POST request to '/login' with valid username and password. 2. Extract ... | HTTP 200 OK response with the user's profile information (username, email) in th... | Happy | Pending |
| TC002 | Attempt to view profile without authentication | 1. Send a GET request to '/profile' without an 'Authorization' header or with an... | HTTP 401 Unauthorized response. | Negative | Pending |
| TC003 | Successfully update user's email address | 1. Send a POST request to '/login' with valid credentials and obtain JWT token. ... | HTTP 200 OK response.  Subsequent GET request to '/profile' should return the up... | Happy | Pending |
| TC004 | Attempt to update with an invalid email format | 1. Send a POST request to '/login' with valid credentials and obtain JWT token. ... | HTTP 400 Bad Request response with an error message indicating the invalid email... | Negative | Pending |
| TC005 | Attempt to update with an existing email address | 1. Send a POST request to '/login' with valid credentials and obtain JWT token. ... | HTTP 400 Bad Request response indicating the email is already in use. | Negative | Pending |
| TC006 | Attempt to update profile with an expired token | 1. Obtain a JWT token. 2. Wait until the token expires. 3. Send a PUT request to... | HTTP 401 Unauthorized response or a response indicating token expiry. | Negative | Pending |
| TC007 | Update with extremely long username (edge case) | 1. Login successfully and obtain a valid JWT token. 2. Send a PUT request to '/p... | Either a HTTP 200 OK if the backend handles long usernames gracefully, or a HTTP... | Edge | Pending |
| TC008 | Update with a username containing special characters (edge case) | 1. Login successfully. 2. Send a PUT request to '/profile' with a JSON payload c... | HTTP 200 OK if allowed, or HTTP 400 Bad Request if special characters are not pe... | Edge | Pending |

## Detailed Test Cases

### TC001: Successfully view user profile information after successful login

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Send a POST request to '/login' with valid username and password. 2. Extract the JWT access token from the response. 3. Send a GET request to '/profile' with the JWT access token in the 'Authorization' header.

**Expected Result:**
HTTP 200 OK response with the user's profile information (username, email) in the JSON response body.

---

### TC002: Attempt to view profile without authentication

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Send a GET request to '/profile' without an 'Authorization' header or with an invalid token.

**Expected Result:**
HTTP 401 Unauthorized response.

---

### TC003: Successfully update user's email address

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Send a POST request to '/login' with valid credentials and obtain JWT token. 2. Send a PUT request to '/profile' with the JWT token in the 'Authorization' header and a JSON payload containing the new, valid email address.

**Expected Result:**
HTTP 200 OK response.  Subsequent GET request to '/profile' should return the updated email address.

---

### TC004: Attempt to update with an invalid email format

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Send a POST request to '/login' with valid credentials and obtain JWT token. 2. Send a PUT request to '/profile' with the JWT token in the 'Authorization' header and a JSON payload containing an invalid email format (e.g., missing '@' symbol).

**Expected Result:**
HTTP 400 Bad Request response with an error message indicating the invalid email format.

---

### TC005: Attempt to update with an existing email address

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Send a POST request to '/login' with valid credentials and obtain JWT token. 2. Send a PUT request to '/profile' with the JWT token and a JSON payload containing an email address already in use by another user.

**Expected Result:**
HTTP 400 Bad Request response indicating the email is already in use.

---

### TC006: Attempt to update profile with an expired token

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Obtain a JWT token. 2. Wait until the token expires. 3. Send a PUT request to '/profile' with the expired token.

**Expected Result:**
HTTP 401 Unauthorized response or a response indicating token expiry.

---

### TC007: Update with extremely long username (edge case)

**Type:** Edge

**Status:** Pending

**Test Steps:**
1. Login successfully and obtain a valid JWT token. 2. Send a PUT request to '/profile' with a JSON payload containing a username exceeding the maximum allowed length (if defined; otherwise, a very long string).

**Expected Result:**
Either a HTTP 200 OK if the backend handles long usernames gracefully, or a HTTP 400 Bad Request with an error message specifying the length limitation.

---

### TC008: Update with a username containing special characters (edge case)

**Type:** Edge

**Status:** Pending

**Test Steps:**
1. Login successfully. 2. Send a PUT request to '/profile' with a JSON payload containing a username with special characters (e.g., !@#$%^&*).

**Expected Result:**
HTTP 200 OK if allowed, or HTTP 400 Bad Request if special characters are not permitted, with an appropriate error message.

---


================================================================================

# Acceptance Criteria Validation Report

**Acceptance Criteria:**
User can view their current profile information including username, email, and account creation date.User can update their email address while maintaining username uniqueness.User can change their password with proper validation of current password.System validates new email format and ensures it's not already in use.System requires re-authentication for sensitive profile changes.System maintains audit trail of profile modifications

**Summary:**
- Total Test Cases: 8
- Satisfied: 3
- Not Satisfied: 5
- Satisfaction Rate: 37.5%

## ✅ Satisfied Test Cases

### Successfully view user profile information after successful login
- **Steps:** 1. Send a POST request to '/login' with valid username and password. 2. Extract the JWT access token from the response. 3. Send a GET request to '/profile' with the JWT access token in the 'Authorization' header.
- **Expected:** HTTP 200 OK response with the user's profile information (username, email) in the JSON response body.

### Successfully update user's email address
- **Steps:** 1. Send a POST request to '/login' with valid credentials and obtain JWT token. 2. Send a PUT request to '/profile' with the JWT token in the 'Authorization' header and a JSON payload containing the new, valid email address.
- **Expected:** HTTP 200 OK response.  Subsequent GET request to '/profile' should return the updated email address.

### Attempt to update with an existing email address
- **Steps:** 1. Send a POST request to '/login' with valid credentials and obtain JWT token. 2. Send a PUT request to '/profile' with the JWT token and a JSON payload containing an email address already in use by another user.
- **Expected:** HTTP 400 Bad Request response indicating the email is already in use.

## ❌ Test Cases Not Satisfying Criteria

### Attempt to view profile without authentication
- **Steps:** 1. Send a GET request to '/profile' without an 'Authorization' header or with an invalid token.
- **Expected:** HTTP 401 Unauthorized response.

### Attempt to update with an invalid email format
- **Steps:** 1. Send a POST request to '/login' with valid credentials and obtain JWT token. 2. Send a PUT request to '/profile' with the JWT token in the 'Authorization' header and a JSON payload containing an invalid email format (e.g., missing '@' symbol).
- **Expected:** HTTP 400 Bad Request response with an error message indicating the invalid email format.

### Attempt to update profile with an expired token
- **Steps:** 1. Obtain a JWT token. 2. Wait until the token expires. 3. Send a PUT request to '/profile' with the expired token.
- **Expected:** HTTP 401 Unauthorized response or a response indicating token expiry.

### Update with extremely long username (edge case)
- **Steps:** 1. Login successfully and obtain a valid JWT token. 2. Send a PUT request to '/profile' with a JSON payload containing a username exceeding the maximum allowed length (if defined; otherwise, a very long string).
- **Expected:** Either a HTTP 200 OK if the backend handles long usernames gracefully, or a HTTP 400 Bad Request with an error message specifying the length limitation.

### Update with a username containing special characters (edge case)
- **Steps:** 1. Login successfully. 2. Send a PUT request to '/profile' with a JSON payload containing a username with special characters (e.g., !@#$%^&*).
- **Expected:** HTTP 200 OK if allowed, or HTTP 400 Bad Request if special characters are not permitted, with an appropriate error message.

