import requests

def get_all_contests():
    base_url = "https://learn-backend-jklu.vercel.app"
    
    # We can fetch courses, then fetch contests for each
    res_c = requests.get(f"{base_url}/courses")
    courses = res_c.json()
    
    found_questions = False
    for course in courses:
        res = requests.get(f"{base_url}/contests/course/{course['id']}")
        contests = res.json()
        for c in contests:
            print(f"Contest {c['id']} for course {course['code']} has {len(c.get('questions', []))} questions.")
            if len(c.get('questions', [])) > 0:
                found_questions = True
                
    if not found_questions:
        print("NO QUESTIONS FOUND IN ANY CONTEST! Might be a bug in fake_sqlalchemy.")
    else:
        print("Some contests have questions, meaning the data fetch logic works.")

if __name__ == "__main__":
    get_all_contests()
