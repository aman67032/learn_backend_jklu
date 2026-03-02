import requests

def test_contests():
    base_url = "https://learn-backend-jklu.vercel.app"
    
    # Check course contests
    res = requests.get(f"{base_url}/contests/course/128")
    print(f"Contests for course 128: Status {res.status_code}")
    try:
        data = res.json()
        print("Data:", data)
    except Exception as e:
        print("Error parsing JSON:", e)
        print("Text:", res.text)
        
    print("\n----------------\n")
    # Check specific contest 20
    res2 = requests.get(f"{base_url}/contests/20")
    print(f"Contest 20: Status {res2.status_code}")
    try:
        data2 = res2.json()
        print("Data:", data2)
    except Exception as e:
        print("Error parsing JSON:", e)
        print("Text:", res2.text)

if __name__ == "__main__":
    test_contests()
