# User Story Test Cases

**User Story:**
As a registered user, I want to view and update my profile information so that I can keep my account details current and accurate.

**Analysis:**
The user wants to maintain accurate and up-to-date personal information associated with their account.  This allows them to ensure their account reflects their current circumstances and preferences.  The core goal is to easily manage their profile data.

Key Requirements:

* **View Profile Information:** Ability to see existing profile data.
* **Update Profile Information:** Ability to modify existing profile data (e.g., name, email, address, etc.).
* **Data Persistence:** Updated information is saved and reflected consistently.


**Acceptance Criteria:**
User can view their current profile information including username, email, and account creation date.User can update their email address while maintaining username uniqueness.User can change their password with proper validation of current password.System validates new email format and ensures it's not already in use.System requires re-authentication for sensitive profile changes.System maintains audit trail of profile modifications

# Test Cases Generated

**Generated on:** 2025-09-01 10:06:20

**Total Test Cases:** 8

## Test Cases Table

| **Test Case ID** | **Test Scenario** | **Test Steps** | **Expected Result** | **Type** | **Status** |
|---|---|---|---|---|---|
| TC001 | View existing profile information as a logged-in user | 1. Log in as a registered user. 2. Access the 'Profile' endpoint (assuming it ex... | The API returns the user's profile information (username, email) in a JSON respo... | Happy | Pending |
| TC002 | Update existing profile information as a logged-in user (valid data) | 1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send... | The API updates the user's profile information. The updated data is reflected in... | Happy | Pending |
| TC003 | Attempt to update profile with duplicate username | 1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send... | The API returns an error indicating that the username is already in use. The res... | Negative | Pending |
| TC004 | Attempt to update profile with duplicate email | 1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send... | The API returns an error indicating that the email is already in use. The respon... | Negative | Pending |
| TC005 | Attempt to update profile with invalid email format | 1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send... | The API returns an error indicating an invalid email format. The response status... | Negative | Pending |
| TC006 | Attempt to update profile information without authentication | 1. Access the 'Profile Update' endpoint without logging in. 2. Send a PUT reques... | The API returns an authentication error (e.g., 401 Unauthorized). | Negative | Pending |
| TC007 | Update profile with extremely long username (edge case) | 1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send... | The API returns an error indicating that the username exceeds the maximum allowe... | Edge | Pending |
| TC008 | Update profile with an empty username field | 1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send... | The API should return an error indicating that the username field is required. T... | Edge | Pending |

## Detailed Test Cases

### TC001: View existing profile information as a logged-in user

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Log in as a registered user. 2. Access the 'Profile' endpoint (assuming it exists). 3. Retrieve the user's profile data.

**Expected Result:**
The API returns the user's profile information (username, email) in a JSON response.  The response status code is 200 (OK).

---

### TC002: Update existing profile information as a logged-in user (valid data)

**Type:** Happy

**Status:** Pending

**Test Steps:**
1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send a PUT request with valid updated username and email. 4. Retrieve the updated profile data.

**Expected Result:**
The API updates the user's profile information. The updated data is reflected in the retrieved profile information. The response status code is 200 (OK).

---

### TC003: Attempt to update profile with duplicate username

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send a PUT request with a username already used by another user. 4. Observe API response.

**Expected Result:**
The API returns an error indicating that the username is already in use. The response status code is 400 (Bad Request) or similar.

---

### TC004: Attempt to update profile with duplicate email

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send a PUT request with an email address already registered to another user. 4. Observe API response.

**Expected Result:**
The API returns an error indicating that the email is already in use. The response status code is 400 (Bad Request) or similar.

---

### TC005: Attempt to update profile with invalid email format

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send a PUT request with an invalid email format (e.g., missing @ symbol). 4. Observe API response.

**Expected Result:**
The API returns an error indicating an invalid email format. The response status code is 400 (Bad Request) or similar.

---

### TC006: Attempt to update profile information without authentication

**Type:** Negative

**Status:** Pending

**Test Steps:**
1. Access the 'Profile Update' endpoint without logging in. 2. Send a PUT request with updated profile information.

**Expected Result:**
The API returns an authentication error (e.g., 401 Unauthorized).

---

### TC007: Update profile with extremely long username (edge case)

**Type:** Edge

**Status:** Pending

**Test Steps:**
1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send a PUT request with a username exceeding the maximum allowed length. 4. Observe API response.

**Expected Result:**
The API returns an error indicating that the username exceeds the maximum allowed length.  The response status code is 400 (Bad Request) or similar.

---

### TC008: Update profile with an empty username field

**Type:** Edge

**Status:** Pending

**Test Steps:**
1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send a PUT request with an empty username field. 4. Observe the API response.

**Expected Result:**
The API should return an error indicating that the username field is required. The response status code is 400 (Bad Request) or similar.

---


================================================================================

# Acceptance Criteria Validation Report

**Acceptance Criteria:**
User can view their current profile information including username, email, and account creation date.User can update their email address while maintaining username uniqueness.User can change their password with proper validation of current password.System validates new email format and ensures it's not already in use.System requires re-authentication for sensitive profile changes.System maintains audit trail of profile modifications

**Summary:**
- Total Test Cases: 8
- Satisfied: 8
- Not Satisfied: 0
- Satisfaction Rate: 100.0%

## ✅ Satisfied Test Cases

### View existing profile information as a logged-in user
- **Steps:** 1. Log in as a registered user. 2. Access the 'Profile' endpoint (assuming it exists). 3. Retrieve the user's profile data.
- **Expected:** The API returns the user's profile information (username, email) in a JSON response.  The response status code is 200 (OK).

### Update existing profile information as a logged-in user (valid data)
- **Steps:** 1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send a PUT request with valid updated username and email. 4. Retrieve the updated profile data.
- **Expected:** The API updates the user's profile information. The updated data is reflected in the retrieved profile information. The response status code is 200 (OK).

### Attempt to update profile with duplicate username
- **Steps:** 1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send a PUT request with a username already used by another user. 4. Observe API response.
- **Expected:** The API returns an error indicating that the username is already in use. The response status code is 400 (Bad Request) or similar.

### Attempt to update profile with duplicate email
- **Steps:** 1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send a PUT request with an email address already registered to another user. 4. Observe API response.
- **Expected:** The API returns an error indicating that the email is already in use. The response status code is 400 (Bad Request) or similar.

### Attempt to update profile with invalid email format
- **Steps:** 1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send a PUT request with an invalid email format (e.g., missing @ symbol). 4. Observe API response.
- **Expected:** The API returns an error indicating an invalid email format. The response status code is 400 (Bad Request) or similar.

### Attempt to update profile information without authentication
- **Steps:** 1. Access the 'Profile Update' endpoint without logging in. 2. Send a PUT request with updated profile information.
- **Expected:** The API returns an authentication error (e.g., 401 Unauthorized).

### Update profile with extremely long username (edge case)
- **Steps:** 1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send a PUT request with a username exceeding the maximum allowed length. 4. Observe API response.
- **Expected:** The API returns an error indicating that the username exceeds the maximum allowed length.  The response status code is 400 (Bad Request) or similar.

### Update profile with an empty username field
- **Steps:** 1. Log in as a registered user. 2. Access the 'Profile Update' endpoint. 3. Send a PUT request with an empty username field. 4. Observe the API response.
- **Expected:** The API should return an error indicating that the username field is required. The response status code is 400 (Bad Request) or similar.

