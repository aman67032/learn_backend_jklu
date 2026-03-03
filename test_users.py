import requests

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@jklu.edu.in"
# We'll use the superadmin to authenticate
# To get the valid admin credentials, we can look at the test scripts

def test_admin_flow():
    # Login as admin
    print("Logging in...")
    login_data = {
        "username": ADMIN_EMAIL,
        "password": "password123"  # Assuming standard test password
    }
    
    r = requests.post(f"{BASE_URL}/admin-login", data=login_data)
    if r.status_code != 200:
        print("Login failed, attempting to register an admin first.")
        r_admin = requests.post(f"{BASE_URL}/create-admin", json={
            "email": "admin@jklu.edu.in",
            "name": "Super Admin",
            "password": "password123"
        })
        print("Create admin:", r_admin.text)
        r = requests.post(f"{BASE_URL}/admin-login", data=login_data)
        if r.status_code != 200:
            print("Failed to login as admin completely", r.text)
            return
            
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful!")

    # Test fetching users
    print("\n--- Testing get users ---")
    r = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    print("Get users:", r.status_code)
    try:
        users = r.json()
        print(f"Found {len(users)} users.")
    except Exception as e:
        print("Failed to parse json. Text:", r.text)
        return
        
    sub_admin_email = "ta_test@jklu.edu.in"
    ta_user = next((u for u in users if u["email"] == sub_admin_email), None)
    
    if not ta_user:
        # Create sub-admin if not exists
        print("\n--- Testing create-sub-admin ---")
        create_data = {
            "email": sub_admin_email,
            "name": "Test TA",
            "password": "password123"
        }
        r = requests.post(f"{BASE_URL}/admin/create-sub-admin", json=create_data, headers=headers)
        print(f"Create sub-admin {sub_admin_email}:", r.status_code, r.text)
        if r.status_code == 200:
            ta_user = r.json()
        else:
            return
            
    print(f"TA User details: Name={ta_user['name']}, Role={ta_user['admin_role']}, IsAdmin={ta_user['is_admin']}")
    print(f"Found {len(users)} users.")
    
    ta_user = next((u for u in users if u["email"] == sub_admin_email), None)
    if not ta_user:
        print("Failed to find the newly created TA user!")
        return
        
    print(f"TA User details: Name={ta_user['name']}, Role={ta_user['admin_role']}, IsAdmin={ta_user['is_admin']}")

    # Test updating a user
    print("\n--- Testing update user ---")
    user_id = ta_user["id"]
    update_data = {
        "is_admin": False,
        "admin_role": None
    }
    r = requests.put(f"{BASE_URL}/admin/users/{user_id}", json=update_data, headers=headers)
    print("Update user to regular student:", r.status_code, r.text)
    
    # Test deleting the user
    print("\n--- Testing delete user ---")
    r = requests.delete(f"{BASE_URL}/admin/users/{user_id}", headers=headers)
    print("Delete user:", r.status_code, r.text)
    
    # Verify deletion
    r = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    deleted_ta = next((u for u in r.json() if u["email"] == sub_admin_email), None)
    print("Verify deletion (Should be None):", deleted_ta)

if __name__ == "__main__":
    test_admin_flow()
