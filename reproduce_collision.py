
import os
import sys

# Mock environment variables
os.environ["DATABASE_URL"] = "mongodb://localhost:27017"
os.environ["SECRET_KEY"] = "test-secret"

# Add current directory to path
sys.path.append(os.getcwd())

from main import ContestQuestion, SessionLocal, DailyContest

def reproduce_id_collision():
    db = SessionLocal()
    try:
        # Create a contest first
        contest = DailyContest(course_id=1, date="Test Day Conflict", title="Test")
        db.add(contest)
        db.commit()
        db.refresh(contest)
        
        print(f"Created contest with ID: {contest.id}")
        
        # Add two questions at once
        q1 = ContestQuestion(contest_id=contest.id, title="Q1", question="Q1", code_snippets={}, explanation="E1")
        q2 = ContestQuestion(contest_id=contest.id, title="Q2", question="Q2", code_snippets={}, explanation="E2")
        
        db.add(q1)
        db.add(q2)
        
        print("Committing two questions...")
        db.commit()
        
        print(f"Q1 ID: {q1.id}")
        print(f"Q2 ID: {q2.id}")
        
        if q1.id == q2.id:
            print("FAILURE CONFIRMED: Q1 and Q2 have the same ID!")
        else:
            print("SUCCESS: Questions have unique IDs (Wait, did they?)")
            
        # Check database count
        count = db.query(ContestQuestion).filter(ContestQuestion.contest_id == contest.id).count()
        print(f"Questions count in DB for contest {contest.id}: {count}")
        
        if count == 1:
            print("FAILURE CONFIRMED: Only one question exists in DB!")
            
    finally:
        db.close()

if __name__ == "__main__":
    reproduce_id_collision()
