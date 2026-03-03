import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
client = MongoClient(DATABASE_URL)
db = client.get_database("paperportal")

def run_check():
    print("--- Latest Contests and Questions ---")
    contests = list(db["daily_contests"].find().sort("_id", -1).limit(5))
    for c in contests:
        cid = c.get("id")
        title = c.get("title", "No Title")
        q_count = db["contest_questions"].count_documents({"contest_id": cid})
        print(f"ID {cid}: {title} -> {q_count} questions")

    # Check for orphaned questions
    orphaned = db["contest_questions"].count_documents({"contest_id": None})
    print(f"\nOrphaned questions (contest_id: None): {orphaned}")

run_check()
