
import requests

BASE_URL = "http://localhost:8000"

def test_delete_announcement():
    # 1. Login
    login_res = requests.post(f"{BASE_URL}/login", json={
        "email": "coding_ta1@jklu.edu.in",
        "password": "ta1_password"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create announcement
    data = {
        "title": "To Be Deleted",
        "content": "This will be deleted"
    }
    res = requests.post(f"{BASE_URL}/admin/coding-announcements", data=data, headers=headers)
    ann_id = res.json()["id"]
    print(f"Created announcement {ann_id}")

    # 3. Verify it exists
    list_res = requests.get(f"{BASE_URL}/coding-announcements")
    anns = list_res.json()
    if any(a["id"] == ann_id for a in anns):
        print(f"Verified announcement {ann_id} exists")
    else:
        print("Failed to find announcement after creation")
        return

    # 4. Delete announcement
    print(f"Deleting announcement {ann_id}...")
    del_res = requests.delete(f"{BASE_URL}/admin/coding-announcements/{ann_id}", headers=headers)
    print(f"Delete response: {del_res.status_code} {del_res.text}")

    # 5. Verify it's gone
    list_res = requests.get(f"{BASE_URL}/coding-announcements")
    anns = list_res.json()
    if any(a["id"] == ann_id for a in anns):
        print(f"❌ FAILURE: Announcement {ann_id} still exists!")
    else:
        print(f"✅ SUCCESS: Announcement {ann_id} deleted!")

if __name__ == "__main__":
    test_delete_announcement()
