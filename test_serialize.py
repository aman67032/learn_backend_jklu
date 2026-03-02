import sys
import traceback
from main import User, serialize_user, db_type, DATABASE_URL
from fake_sqlalchemy import FakeModelInstance

def test_exception():
    try:
        # Create a mock user dict like Mongo would return
        user_dict = {
            "id": 1,
            "email": "test@jklu.edu.in",
            "name": "Test",
            "is_admin": False,
            "email_verified": True,
            "created_at": "2026-03-02T10:00:00Z"
        }
        
        # Instantiate FakeModelInstance
        user = FakeModelInstance(user_dict, User)
        
        # simulate setattr in update_profile
        setattr(user, "roll_no", "123")
        setattr(user, "student_id", "STUD123")
        with open("user_state.txt", "w") as f:
            f.write(str(user.__dict__))
        
        # Test serialize_user
        print("Serializing...")
        result = serialize_user(user)
        print("Serialized:", result)
        
        # Test UserResponse instantiation
        from main import UserResponse
        print("Instantiating UserResponse...")
        resp = UserResponse(**result)
        print(resp)
        
    except Exception as e:
        with open("error_trace.txt", "w") as f:
            traceback.print_exc(file=f)
        traceback.print_exc()

if __name__ == "__main__":
    test_exception()
