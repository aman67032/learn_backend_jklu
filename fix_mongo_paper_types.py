import os
from dotenv import load_dotenv
from fake_sqlalchemy import create_engine

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
db = engine.client.get_database("paperportal")
collection = db["papers"]

papers = collection.find()
updated = 0

for p in papers:
    paper_type = p.get('paper_type')
    if paper_type and paper_type.isupper():
        collection.update_one({'_id': p['_id']}, {'$set': {'paper_type': paper_type.lower()}})
        updated += 1
        print(f"Updated paper ID: {p.get('id')} to lowercase '{paper_type.lower()}'")

print(f"Total updated: {updated}")
