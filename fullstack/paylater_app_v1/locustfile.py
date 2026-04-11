# locustfile.py
#
# To run this load test:
# 1. Make sure your FastAPI application is running.
# 2. Install Locust: pip install locust
# 3. Update the email and password in the on_start method below with a valid test user.
# 4. Run from your terminal: locust -f locustfile.py
# 5. Open your browser to http://localhost:8089 and start the test.

from locust import HttpUser, task, between
import random
import time


class PayLaterUser(HttpUser):
    """
    Represents a virtual user for the Pay-Later application.

    This user will first log in to get an authentication token and then
    repeatedly perform common tasks like creating transactions and checking dues.
    """
    # Each simulated user will wait between 1 and 3 seconds after each task.
    wait_time = between(1, 3)
    auth_token = None
    headers = {}
    backoff = 1

    def on_start(self):
        """
        This method is called when a virtual user is started.
        It simulates the login process to get an access token for other requests.
        """
        # --- IMPORTANT ---
        # Replace these with the credentials of a real user in your database.
        # For a more advanced test, you could use a list of users.
        credentials = {
            "email": "abhi@gmail.com",
            "password": "abhi123"
        }

        # try:
        #     # Send the login request
        #     response = self.client.post("/token(login)", json=credentials, name="/token(login)")
        #     response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        #     # Extract the token and set it for future requests
        #     self.auth_token = response.json()["access_token"]
        #     self.headers = {"X-Access-Token": self.auth_token}
        #     print(f"User logged in, token received: {self.auth_token[:10]}...")

        # except Exception as e:
        #     print(f"Failed to login and get token: {e}")
        #     # If login fails, we can stop the user from proceeding.
        #     self.stop()
        for attempt in range(5):  # try 5 times
            response = self.client.post("/token(login)", json=credentials, name="/token(login)")
            if response.status_code == 200:
                self.auth_token = response.json()["access_token"]
                self.headers = {"X-Access-Token": self.auth_token}
                print(f"User logged in. Token: {self.auth_token[:10]}...")
                return
            elif response.status_code == 429:
                print(f"Login rate-limited (429). Waiting before retrying... [Attempt {attempt+1}]")
                time.sleep(2 * (attempt + 1))  # exponential backoff
            else:
                print(f"Login failed with {response.status_code}: {response.text}")
                self.stop()
                return

        print("Login failed after retries. Stopping user.")
        self.stop()
        
    @task(3)  # This task will be executed 3 times more often than the other task
    def create_transaction(self):
        """
        Simulates a user making a purchase. This requires authentication.
        """
        # if self.auth_token:
        #     # Define the data for a new transaction
        #     transaction_data = {
        #         "merchant_name": "KFC", # Make sure this merchant exists
        #         "amount": round(random.uniform(5.0, 150.0), 2) # Use a random amount
        #     }

        #     # Send the POST request with the authentication header
        #     self.client.post(
        #         "/transactions",
        #         json=transaction_data,
        #         headers=self.headers,
        #         name="/transactions"  # Group stats under this name in the UI
        #     )
        """Make a purchase, handle rate-limiting."""
        if not self.auth_token:
            return

        data = {
            "merchant_name": "KFC",
            "amount": round(random.uniform(5.0, 150.0), 2)
        }

        response = self.client.post("/transactions", json=data, headers=self.headers, name="/transactions")
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", self.backoff))
            print(f"Transaction hit rate limit (429). Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            self.backoff = min(self.backoff * 2, 60)  # double backoff, cap at 60s
        else:
            self.backoff = 1  # reset backoff on success
            
    @task(1) # This task will be executed less often
    def get_my_dues(self):
        """
        Simulates a user checking their current dues. This requires authentication.
        """
        if not self.auth_token:
            return

        response = self.client.get("/report/me/dues", headers=self.headers, name="/report/me/dues")
        if response.status_code == 429:
            print("Dues check rate-limited (429). Will try again later.")

    def on_stop(self):
        """
        This method is called when a virtual user is stopped.
        """
        print("User session stopping.")