import os
from dotenv import load_dotenv
from fake_sqlalchemy import create_engine

load_dotenv()

def check_db():
    url = os.getenv("DATABASE_URL")
    if not url:
        print("NO DATABASE_URL in .env")
        return
        
    engine = create_engine(url)
    db = engine.db
    
    # Check what collections exist
    try:
        collections = db.list_collection_names()
        print("Collections in DB:", collections)
        
        # Check contests
        contests_count = db["daily_contests"].count_documents({})
        print(f"Daily contests count: {contests_count}")
        
        # Check questions
        q_count = db["contest_questions"].count_documents({})
        print(f"Contest questions count: {q_count}")
        
        if q_count > 0:
            first_q = db["contest_questions"].find_one()
            print("First question sample:", first_q)
            print(f"Question contest_id type: {type(first_q.get('contest_id'))}")
            
            # Find a contest ID that matches
            cid = first_q.get("contest_id")
            contest = db["daily_contests"].find_one({"id": cid})
            if contest:
                print(f"Matched contest id type: {type(contest.get('id'))}")
            else:
                print(f"Orphaned question: contest_id {cid} not found in daily_contests")
                
    except Exception as e:
        print("Error connecting/querying:", e)

if __name__ == "__main__":
    check_db()
