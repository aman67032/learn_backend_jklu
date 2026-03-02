import os
from dotenv import load_dotenv
from fake_sqlalchemy import create_engine

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
db = engine.client.get_database("paperportal")
papers = db["papers"].find().limit(10)

for p in papers:
    print(f"ID: {p.get('id')}, Type: {p.get('paper_type')}, Status: {p.get('status')}")
