import os
from main import get_db, DailyContest, ContestQuestion
from fake_sqlalchemy import Session
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
client = MongoClient(DATABASE_URL)
db_mongo = client.get_database("paperportal")
db = Session(db_mongo)

def test_creation():
    print("--- Testing Contest Creation Flow ---")
    
    # 1. Start a "transaction"
    new_contest = DailyContest(
        course_id=127,
        date="Test Date " + os.urandom(4).hex(),
        title="Test Contest",
        description="Testing flush"
    )
    
    db.add(new_contest)
    print(f"Before flush, contest ID: {new_contest.id}")
    
    # 2. Flush to get ID
    db.flush()
    print(f"After flush, contest ID: {new_contest.id}")
    
    if new_contest.id is None:
        print("❌ FAILED: Contest ID still None after flush")
        return

    # 3. Create question using contest ID
    new_q = ContestQuestion(
        contest_id=new_contest.id,
        order=1,
        title="Test Question",
        question="What is 1+1?",
        explanation="2"
    )
    db.add(new_q)
    
    # 4. Commit
    db.commit()
    print("Committed.")

    # 5. Verify in DB
    saved_q = db_mongo["contest_questions"].find_one({"title": "Test Question", "contest_id": new_contest.id})
    if saved_q:
        print(f"SUCCESS: Question saved with contest_id {saved_q['contest_id']}")
    else:
        print("FAILED: Question not found with correct contest_id")
        # Check if it was saved with None
        orphaned = db_mongo["contest_questions"].find_one({"title": "Test Question", "contest_id": None})
        if orphaned:
             print("Found orphaned question with contest_id=None")

test_creation()
