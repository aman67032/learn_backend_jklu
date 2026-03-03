import requests
import json
import base64

BASE_URL = "http://localhost:8000"

def test_contest_update():
    print("\nTesting Contest Update...")
    # 1. Get an existing contest (using contest 1 if exists or fetching all)
    res = requests.get(f"{BASE_URL}/admin/contests")
    if res.status_code != 200:
        print(f"Error fetching contests: {res.status_code}")
        return
    
    contests = res.json()
    if not contests:
        print("No contests found to test update.")
        return
    
    contest = contests[0]
    contest_id = contest['id']
    print(f"Updating contest {contest_id}...")
    
    # 2. Add/Modify a question in the payload
    payload = {
        "title": contest['title'] + " (Updated)",
        "questions": [
            {
                "order": 1,
                "title": "New Test Question",
                "question": "What is 2+2?",
                "code_snippets": {"python": "print(4)"},
                "explanation": "Simple math"
            }
        ]
    }
    
    # We need an admin token. Assuming the local dev env doesn't strictly enforce tokens or we use one if provided.
    # For local test, we'll try without if it's open, or user might need to provide one.
    # Note: require_coding_admin checks for admin_role.
    headers = {} # Token would go here
    
    update_res = requests.put(f"{BASE_URL}/contests/{contest_id}", json=payload, headers=headers)
    print(f"Update Result: {update_res.status_code}")
    if update_res.status_code == 200:
        updated_data = update_res.json()
        print(f"Updated Title: {updated_data['title']}")
        print(f"Questions Count: {len(updated_data['questions'])}")
    else:
        print(f"Update Failed: {update_res.text}")

def test_announcement_upload():
    print("\nTesting Announcement Upload...")
    url = f"{BASE_URL}/admin/coding-announcements"
    data = {
        "title": "Test Announcement",
        "content": "This is a test announcement with a file."
    }
    files = {
        "file": ("test.txt", b"Hello world content", "text/plain")
    }
    
    res = requests.post(url, data=data, files=files)
    print(f"Upload Result: {res.status_code}")
    if res.status_code == 200:
        ann = res.json()
        print(f"Announcement ID: {ann['id']}")
        print(f"File Name: {ann['file_name']}")
        
        # Test download
        dl_url = f"{BASE_URL}/coding-announcements/{ann['id']}/download"
        dl_res = requests.get(dl_url)
        print(f"Download Result: {dl_res.status_code}")
        if dl_res.status_code == 200:
            print(f"Downloaded Content: {dl_res.text}")
    else:
        print(f"Upload Failed: {res.text}")

if __name__ == "__main__":
    # Note: These tests assume the server is running locally on port 8000
    # and that authentication is bypassed or handled via headers.
    try:
        test_contest_update()
        test_announcement_upload()
    except Exception as e:
        print(f"Test execution failed: {e}")
