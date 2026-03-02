import sys
from main import User
from fake_sqlalchemy import FakeModelInstance, Session

def test_fixes():
    class DummyDB:
        class DummyCollection:
            def find(self, *args, **kwargs):
                class Cursor:
                    def sort(self, *a, **k): return self
                    def limit(self, *a, **k): return self
                    def skip(self, *a, **k): return self
                    def __iter__(self): yield {"_id": "mongoid", "id": 1, "email": "test@jklu"}
                return Cursor()
            def update_one(self, filter_doc, update_doc, upsert=False):
                print("UPDATE CALLED:", filter_doc, update_doc)
            def find_one(self, query):
                return {"_id": "mongoid", "id": 1, "email": "test@jklu", "roll_no": "999"}
                
        def __getitem__(self, name):
            print("Accessing DB Collection:", name)
            if not isinstance(name, str):
                raise TypeError("name must be an instance of str")
            return self.DummyCollection()

    session = Session(DummyDB())
    
    # 1. Test Query fetching and tracking
    user = session.query(User).filter(User.id == 1).first()
    print("Fetched user:", user)
    print("User in tracked objects:", user in session._new_objects)
    
    # 2. Test Tablename fix (will crash if None)
    session.refresh(user) 
    print("Refresh success!")
    
    # 3. Test Commit updates existing fetched objects
    setattr(user, "roll_no", "123")
    session.commit()
    print("Commit success!")
    
if __name__ == "__main__":
    test_fixes()
