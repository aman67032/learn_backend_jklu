import os
from dotenv import load_dotenv
from fake_sqlalchemy import create_engine, Session, FakeModelInstance
from main import DailyContest

load_dotenv()

def test_fetch():
    url = os.getenv("DATABASE_URL")
    if not url:
        print("NO DATABASE_URL in .env")
        return
        
    engine = create_engine(url)
    session = Session(engine.db)
    
    # query contest 20
    contest = session.query(DailyContest).filter(DailyContest.id == 20).first()
    if not contest:
        print("Contest 20 not found.")
        return
        
    print(f"Contest 20 fetched: {contest.title}")
    
    # Try fetching questions
    questions = getattr(contest, "questions", None)
    print(f"Questions fetched: {len(questions) if questions else 0}")
    if questions:
        for q in questions:
            print(f" - Q{q.id}: {q.title}")
            
if __name__ == "__main__":
    test_fetch()
