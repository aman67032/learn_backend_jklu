from main import register, update_profile, SessionLocal, RegisterRequest, ProfileUpdate
import uuid

def test_functions():
    db = SessionLocal()
    unique_email = f"test_{uuid.uuid4().hex[:8]}@jklu.edu.in"
    print(f"Testing register with {unique_email}...")
    
    req = RegisterRequest(
        email=unique_email,
        name="Test User",
        password="password123",
        confirm_password="password123"
    )
    
    try:
        res = register(request=req, db=db)
        print("Register Success!")
        print("User data:", res)
        
        # Test profile update
        print("Testing profile update...")
        # from main import User
        user = res["user"] # It's a dict or UserResponse? Wait, UserResponse is a BaseModel. 
        # But wait, register returns a dict that gets converted to RegisterVerifyResponse by FastAPI
        if isinstance(res, dict):
            current_user = res["user"]
        else:
            current_user = res.user
            
        print("current user:", current_user)
        # We need the actual User object from the DB, not the response model, to pass to update_profile
        from main import get_current_user_optional, User
        db_user = db.query(User).filter(User.email == unique_email).first()
        
        prof_req = ProfileUpdate(roll_no="12345", student_id="STU123")
        prof_res = update_profile(update=prof_req, db=db, current_user=db_user)
        print("Profile Update Success!")
        print("New profile data:", prof_res)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_functions()
