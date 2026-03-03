
import os
import sys

# Mock environment variables
os.environ["DATABASE_URL"] = "mongodb://localhost:27017"
os.environ["SECRET_KEY"] = "test-secret"

# Add current directory to path
sys.path.append(os.getcwd())

from main import ContestQuestion, SessionLocal, DailyContest

def verify_orphaned_questions():
    db = SessionLocal()
    try:
        # 1. Create a contest and a question
        print("Creating contest and question...")
        contest = DailyContest(course_id=1, date="Delete Test", title="Delete Test")
        db.add(contest)
        db.flush()
        
        q = ContestQuestion(contest_id=contest.id, title="Test Q", question="Q", code_snippets={}, explanation="E")
        db.add(q)
        db.commit()
        db.refresh(contest)
        
        contest_id = contest.id
        print(f"Contest ID: {contest_id}")
        
        # 2. Verify they exist
        q_count = db.query(ContestQuestion).filter(ContestQuestion.contest_id == contest_id).count()
        print(f"Initial questions count: {q_count}")
        
        # 3. Delete the contest using the same logic as the endpoint
        print("Deleting contest...")
        contest_to_del = db.query(DailyContest).filter(DailyContest.id == contest_id).first()
        db.delete(contest_to_del)
        db.commit()
        
        # 4. Check if contest is gone
        deleted_contest = db.query(DailyContest).filter(DailyContest.id == contest_id).first()
        print(f"Contest still exists? {'Yes' if deleted_contest else 'No'}")
        
        # 5. Check if questions are still there
        remaining_q_count = db.query(ContestQuestion).filter(ContestQuestion.contest_id == contest_id).count()
        print(f"Remaining questions count: {remaining_q_count}")
        
        if remaining_q_count > 0:
            print("FAILURE CONFIRMED: Questions were NOT deleted (orphaned)!")
        else:
            print("SUCCESS: Questions were deleted with the contest.")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_orphaned_questions()
