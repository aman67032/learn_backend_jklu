import requests
import uuid

def test_live():
    base_url = "https://learn-backend-jklu.vercel.app"
    unique_email = f"test_{uuid.uuid4().hex[:8]}@jklu.edu.in"
    
    print(f"Testing REGISTER with {unique_email}...")
    req_data = {
        "email": unique_email,
        "name": "Live Test",
        "password": "password123",
        "confirm_password": "password123"
    }
    
    res = requests.post(f"{base_url}/register", json=req_data)
    print("Register Status:", res.status_code)
    print("Register Body:", res.text)
    
    if res.status_code != 200:
        return
        
    token = res.json().get("access_token")
    
    print("\nTesting ME endpoint...")
    res_me = requests.get(f"{base_url}/me", headers={"Authorization": f"Bearer {token}"})
    print("Me Status:", res.status_code)
    print("Me Body:", res_me.text)
        
    print("\nTesting PROFILE PUT endpoint...")
    prof_data = {"roll_no": "123", "student_id": "STUD123"}
    res_prof = requests.put(f"{base_url}/profile", json=prof_data, headers={"Authorization": f"Bearer {token}"})
    print("Profile Update Status:", res_prof.status_code)
    print("Profile Update Body:", res_prof.text)

if __name__ == "__main__":
    test_live()
