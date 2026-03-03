import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
client = MongoClient(DATABASE_URL)
db = client.get_database("paperportal")

with open(r"c:\Users\MSI1\Downloads\New folder (3)\New folder\db_migration\db_data\contest_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

target_contest_ids = [20, 21]
to_restore = [q for q in questions if q["contest_id"] in target_contest_ids]

print(f"Found {len(to_restore)} questions to restore.")

for q in to_restore:
    # Remove _id if it exists to let Mongo generate a new one
    q.pop("_id", None)
    
    # Check if a question with this title already exists in this contest to avoid duplicates
    existing = db.contest_questions.find_one({"contest_id": q["contest_id"], "title": q["title"]})
    if not existing:
        db.contest_questions.insert_one(q)
        print(f"✅ Restored: {q['title']} (Contest {q['contest_id']})")
    else:
        print(f"⏭️  Already exists: {q['title']} (Contest {q['contest_id']})")

print("Restoration complete.")
