import requests
endpoints = ['/api/wake', '/wake', '/admin-login']
for e in endpoints:
    url = f"https://learn-backend-jklu.vercel.app{e}"
    print(f"\n--- {url} ---")
    try:
        r = requests.post(url, json={}) if 'login' in e else requests.get(url)
        print(f"Status: {r.status_code}")
        print(f"Body: {r.text[:500]}")
    except Exception as ex:
        print(f"Failed: {ex}")
