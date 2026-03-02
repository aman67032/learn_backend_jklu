from fastapi.testclient import TestClient
from main import app
import string
import random

client = TestClient(app)

# Generate random email to avoid collision
rand_str = ''.join(random.choices(string.ascii_lowercase, k=8))
email = f"test_{rand_str}@jklu.edu.in"

response = client.post(
    "/register",
    json={
        "email": email,
        "name": "Test User",
        "password": "password123",
        "confirm_password": "password123"
    }
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

assert response.status_code == 200, "Registration failed"
assert "id" in response.json()["user"], "ID missing from response user"
assert response.json()["user"]["id"] is not None, "ID is None in response user"
print("SUCCESS: Registration endpoint returned a valid ID")
