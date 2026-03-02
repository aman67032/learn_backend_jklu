
from fastapi.testclient import TestClient
from main import app, get_db, Base, engine
import uuid

# Setup test db
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_register_and_profile():
    unique_email = f"test_{uuid.uuid4().hex[:8]}@jklu.edu.in"
    print(f"Registering {unique_email}...")
    
    # 1. Register
    response = client.post("/register", json={
        "email": unique_email,
        "name": "Test User",
        "password": "password123",
        "confirm_password": "password123"
    })
    print("Register response:", response.status_code)
    print("Register body:", response.text)
    
    if response.status_code != 200:
        return
        
    token = response.json()["access_token"]
    
    # 2. Profile update
    print("Updating profile...")
    response = client.put("/profile", 
        json={"roll_no": "12345", "student_id": "STU123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    print("Profile response:", response.status_code)
    print("Profile body:", response.text)

if __name__ == "__main__":
    test_register_and_profile()
