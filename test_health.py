import requests

def test_health():
    base_url = "https://learn-backend-jklu.vercel.app"
    res = requests.get(f"{base_url}/health")
    data = res.json()
    print("Database Config:", data.get("database"))

if __name__ == "__main__":
    test_health()
