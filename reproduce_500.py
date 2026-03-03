
import os
import sys
from datetime import datetime

# Mock environment variables
os.environ["DATABASE_URL"] = "mongodb://localhost:27017"
os.environ["SECRET_KEY"] = "test-secret"

# Add current directory to path so we can import main and fake_sqlalchemy
sys.path.append(os.getcwd())

from main import DailyContest, ContestQuestion, SessionLocal, Course, QuestionCreate, ContestCreate, QuestionResponse, ContestResponse
import fake_sqlalchemy

def reproduce():
    db = SessionLocal()
    try:
        # 1. Ensure a course exists
        course = db.query(Course).first()
        if not course:
            course = Course(code="TEST101", name="Test Course")
            db.add(course)
            db.commit()
            db.refresh(course)
        
        course_id = course.id
        date_str = f"Test Day {datetime.now().timestamp()}"
        
        # 2. Simulate create_contest logic
        print(f"Creating contest for course {course_id} on {date_str}...")
        
        db_contest = DailyContest(
            course_id=course_id,
            date=date_str,
            title="Test Contest",
            description="Test Description"
        )
        db.add(db_contest)
        db.flush()
        
        q_data = {
            "title": "Test Q",
            "question": "What is 1+1?",
            "code_snippets": {"python": "print(2)"},
            "explanation": "Math",
            "order": 1
        }
        
        db_question = ContestQuestion(
            contest_id=db_contest.id,
            **q_data
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_contest)
        
        print(f"Contest created with ID: {db_contest.id}")
        print(f"Type of db_contest: {type(db_contest)}")
        
        # 3. Access questions - THIS IS WHERE WE EXPECT IT TO FAIL
        print("Attempting to access db_contest.questions...")
        questions = db_contest.questions
        print(f"questions: {questions}")
        
        if questions is None:
            print("FAILURE CONFIRMED: db_contest.questions is None!")
        else:
            print(f"SUCCESS: Found {len(questions)} questions")
            
    finally:
        db.close()

if __name__ == "__main__":
    reproduce()
