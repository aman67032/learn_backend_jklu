import sys
from main import User
from fake_sqlalchemy import FakeModelInstance

def test_tablename():
    data = {"id": 1}
    user = FakeModelInstance(data, User)
    
    print("user.__tablename__ is:", user.__tablename__)

if __name__ == "__main__":
    test_tablename()
