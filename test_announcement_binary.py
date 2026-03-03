
import requests
import io

BASE_URL = "http://localhost:8000"

def test_binary_announcement():
    # 1. Login
    login_res = requests.post(f"{BASE_URL}/login", json={
        "email": "coding_ta1@jklu.edu.in",
        "password": "ta1_password"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create announcement with file
    file_content = b"This is a test binary content " + os.urandom(10)
    files = {
        "file": ("test.txt", io.BytesIO(file_content), "text/plain")
    }
    data = {
        "title": "Binary Test",
        "content": "Testing binary storage"
    }
    
    print("Creating announcement...")
    res = requests.post(f"{BASE_URL}/admin/coding-announcements", data=data, files=files, headers=headers)
    if res.status_code != 200:
        print(f"Error creating: {res.status_code} {res.text}")
        return
    
    ann_id = res.json()["id"]
    print(f"Created announcement {ann_id}")

    # 3. Download file
    print("Downloading file...")
    dl_res = requests.get(f"{BASE_URL}/coding-announcements/{ann_id}/download")
    if dl_res.status_code == 200:
        if dl_res.content == file_content:
            print("✅ SUCCESS: Downloaded exact binary content!")
        else:
            print(f"❌ FAILURE: Content mismatch. Expected {len(file_content)} bytes, got {len(dl_res.content)}")
    else:
        print(f"❌ FAILURE: Download status {dl_res.status_code} {dl_res.text}")

if __name__ == "__main__":
    import os
    test_binary_announcement()
