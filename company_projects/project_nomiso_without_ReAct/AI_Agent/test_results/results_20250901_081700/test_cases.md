# User Story Test Cases

**User Story:**
As a registered user, I want to view and update my profile information so that I can keep my account details current and accurate.

**Analysis:**
The user wants to maintain accurate and up-to-date personal information associated with their registered account.  This allows them to control their account details and ensure the information is correct.  The primary goal is self-service management of personal profile data.


Key Requirements:

* **View Profile Information:** Ability to access and display existing profile data.
* **Update Profile Information:** Ability to modify existing profile data (e.g., name, email, address, etc.).
* **Data Persistence:** Changes made to the profile are saved and reflected consistently.
* **Authentication:**  User must be a registered and logged-in user to access and modify their profile.


**Acceptance Criteria:**
User can view their current profile information including username, email, and account creation date.User can update their email address while maintaining username uniqueness.User can change their password with proper validation of current password.System validates new email format and ensures it's not already in use.System requires re-authentication for sensitive profile changes.System maintains audit trail of profile modifications

# Test Cases Generated

**Generated on:** 2025-09-01 08:17:07

**Total Test Cases:** 8

## Test Cases Table

| **Test Case ID** | **Test Scenario** | **Test Steps** | **Expected Result** | **Type** | **Status** |
|---|---|---|---|---|---|
| TC001 | Successfully view profile information as a logged-in user | 1. Login as a registered user. 2. Access the profile endpoint (e.g., GET /profil... | The API returns a 200 OK status code and a JSON payload containing the user's us... | Happy | Pending |
| TC002 | Unsuccessful profile view attempt due to unauthenticated access | 1. Access the profile endpoint (e.g., GET /profile) without logging in. 2. Obser... | The API returns a 401 Unauthorized status code. | Negative | Pending |
| TC003 | Successfully update profile email address | 1. Log in as a registered user. 2. Send a PUT request to the profile endpoint (e... | The API returns a 200 OK status code, and the user's email address is successful... | Happy | Pending |
| TC004 | Unsuccessful email update due to duplicate email | 1. Log in as a registered user. 2. Send a PUT request to the profile endpoint wi... | The API returns a 400 Bad Request status code, indicating the email is already i... | Negative | Pending |
| TC005 | Unsuccessful profile update due to invalid email format | 1. Log in as a registered user. 2. Send a PUT request to the profile endpoint wi... | The API returns a 400 Bad Request status code, indicating an invalid email forma... | Negative | Pending |
| TC006 | Attempt to update profile without authentication | 1. Send a PUT request to the profile endpoint without a valid JWT token. 2. Obse... | The API returns a 401 Unauthorized status code. | Negative | Pending |
| TC007 | Successfully update username (with unique username) | 1. Log in. 2. Send PUT request to /profile with a new, unique username. 3. Verif... | 200 OK, username updated in database. | Happy | Pending |
| TC008 | Fail to update username (with existing username) | 1. Log in. 2. Send PUT request to /profile with an existing username. 3. Observe... | 400 Bad Request, indicating username already exists. | Negative | Pending |

## Detailed Test Cases

### TC001: Successfully view profile information as a logged-in user

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Login as a registered user. 2. Access the profile endpoint (e.g., GET /profile). 3. Verify the response contains the user's username and email.

**Expected Result:**
The API returns a 200 OK status code and a JSON payload containing the user's username and email.

---

### TC002: Unsuccessful profile view attempt due to unauthenticated access

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Access the profile endpoint (e.g., GET /profile) without logging in. 2. Observe the response.

**Expected Result:**
The API returns a 401 Unauthorized status code.

---

### TC003: Successfully update profile email address

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Log in as a registered user. 2. Send a PUT request to the profile endpoint (e.g., PUT /profile) with a valid new email address. 3. Verify the response and check if the email was updated in the database.

**Expected Result:**
The API returns a 200 OK status code, and the user's email address is successfully updated in the database.

---

### TC004: Unsuccessful email update due to duplicate email

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Log in as a registered user. 2. Send a PUT request to the profile endpoint with an email address already in use. 3. Observe the response.

**Expected Result:**
The API returns a 400 Bad Request status code, indicating the email is already in use.

---

### TC005: Unsuccessful profile update due to invalid email format

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Log in as a registered user. 2. Send a PUT request to the profile endpoint with an invalid email format (e.g., missing @ symbol). 3. Observe the response.

**Expected Result:**
The API returns a 400 Bad Request status code, indicating an invalid email format.

---

### TC006: Attempt to update profile without authentication

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Send a PUT request to the profile endpoint without a valid JWT token. 2. Observe the response.

**Expected Result:**
The API returns a 401 Unauthorized status code.

---

### TC007: Successfully update username (with unique username)

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Log in. 2. Send PUT request to /profile with a new, unique username. 3. Verify response and database.

**Expected Result:**
200 OK, username updated in database.

---

### TC008: Fail to update username (with existing username)

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Log in. 2. Send PUT request to /profile with an existing username. 3. Observe response.

**Expected Result:**
400 Bad Request, indicating username already exists.

---


================================================================================

# Acceptance Criteria Validation Report

**Acceptance Criteria:**
User can view their current profile information including username, email, and account creation date.User can update their email address while maintaining username uniqueness.User can change their password with proper validation of current password.System validates new email format and ensures it's not already in use.System requires re-authentication for sensitive profile changes.System maintains audit trail of profile modifications

**Summary:**
- Total Test Cases: 8
- Satisfied: 4
- Not Satisfied: 4
- Satisfaction Rate: 50.0%

## ✅ Satisfied Test Cases

### Successfully view profile information as a logged-in user
- **Steps:** 1. Login as a registered user. 2. Access the profile endpoint (e.g., GET /profile). 3. Verify the response contains the user's username and email.
- **Expected:** The API returns a 200 OK status code and a JSON payload containing the user's username and email.

### Successfully update profile email address
- **Steps:** 1. Log in as a registered user. 2. Send a PUT request to the profile endpoint (e.g., PUT /profile) with a valid new email address. 3. Verify the response and check if the email was updated in the database.
- **Expected:** The API returns a 200 OK status code, and the user's email address is successfully updated in the database.

### Unsuccessful email update due to duplicate email
- **Steps:** 1. Log in as a registered user. 2. Send a PUT request to the profile endpoint with an email address already in use. 3. Observe the response.
- **Expected:** The API returns a 400 Bad Request status code, indicating the email is already in use.

### Unsuccessful profile update due to invalid email format
- **Steps:** 1. Log in as a registered user. 2. Send a PUT request to the profile endpoint with an invalid email format (e.g., missing @ symbol). 3. Observe the response.
- **Expected:** The API returns a 400 Bad Request status code, indicating an invalid email format.

## ❌ Test Cases Not Satisfying Criteria

### Unsuccessful profile view attempt due to unauthenticated access
- **Steps:** 1. Access the profile endpoint (e.g., GET /profile) without logging in. 2. Observe the response.
- **Expected:** The API returns a 401 Unauthorized status code.

### Attempt to update profile without authentication
- **Steps:** 1. Send a PUT request to the profile endpoint without a valid JWT token. 2. Observe the response.
- **Expected:** The API returns a 401 Unauthorized status code.

### Successfully update username (with unique username)
- **Steps:** 1. Log in. 2. Send PUT request to /profile with a new, unique username. 3. Verify response and database.
- **Expected:** 200 OK, username updated in database.

### Fail to update username (with existing username)
- **Steps:** 1. Log in. 2. Send PUT request to /profile with an existing username. 3. Observe response.
- **Expected:** 400 Bad Request, indicating username already exists.

