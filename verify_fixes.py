import os
from main import get_db, DailyContest, ContestQuestion
from fake_sqlalchemy import Session
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Setup session manually to match main.py
DATABASE_URL = os.getenv("DATABASE_URL")
client = MongoClient(DATABASE_URL)
db_mongo = client.get_database("paperportal")
db = Session(db_mongo)

def verify_contest(contest_id):
    print(f"--- Verifying Contest {contest_id} ---")
    contest = db.query(DailyContest).filter(DailyContest.id == contest_id).first()
    if not contest:
        print(f"❌ Contest {contest_id} not found!")
        return
    
    print(f"Contest: {contest.title}")
    questions = contest.questions
    if questions is None:
        print("❌ Relationship 'questions' returned None!")
    else:
        print(f"Count: {len(questions)}")
        for q in questions:
            print(f" - [{q.order}] {q.title} (ID: {q.id})")

verify_contest(20)
verify_contest(21)
