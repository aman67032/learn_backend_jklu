import os
from pymongo import MongoClient
import urllib.parse

# Dummy Base
class Base:
    metadata = type("Metadata", (), {"create_all": lambda *a, **k: None})()
    
    def __init__(self, **kwargs):
        # Apply defaults for missing attributes attached to the model class (prevent Column leakage)
        for k in dir(self.__class__):
            if not k.startswith("_"):
                attr = getattr(self.__class__, k)
                if getattr(attr, "__class__", None) and attr.__class__.__name__ == 'Column':
                    if attr.default is not None:
                        val = attr.default() if callable(attr.default) else attr.default
                        setattr(self, k, val)
                    else:
                        setattr(self, k, None)

        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def dict(self):
        """Serialize model instance to dict for MongoDB insertion."""
        d = {}
        for k in list(vars(self).keys()):
            if not k.startswith("_"):
                d[k] = getattr(self, k)
        d.pop("metadata", None)
        return d
    
def declarative_base():
    return Base

class Column:
    def __init__(self, *args, **kwargs):
        self.primary_key = kwargs.get("primary_key", False)
        self.default = kwargs.get("default", None)
        self.name = None # assigned by metaclass in real SA, we'll hack it out
        self.type_ = args[0] if args else None
        
    def __eq__(self, other):
        return Condition(self, "==", other)
    def __ne__(self, other):
        return Condition(self, "!=", other)
    def __lt__(self, other):
        return Condition(self, "<", other)
    def __le__(self, other):
        return Condition(self, "<=", other)
    def __gt__(self, other):
        return Condition(self, ">", other)
    def __ge__(self, other):
        return Condition(self, ">=", other)
    def in_(self, other):
        return Condition(self, "in", other)
    def ilike(self, other):
        return Condition(self, "ilike", other)
    def like(self, other):
        return Condition(self, "ilike", other) # map like to ilike for simplicity in mongo Regex
    def desc(self):
        return (self, -1)
    def asc(self):
        return (self, 1)
    def isnot(self, other):
        return Condition(self, "isnot", other)
    def is_(self, other):
        return Condition(self, "is", other)

class Condition:
    def __init__(self, field, op, val):
        self.field = field
        self.op = op
        self.val = val

def or_(*conditions):
    return {"$or": [c for c in conditions]}

def and_(*conditions):
    return {"$and": [c for c in conditions]}

class inspect:
    def __init__(self, engine):
        pass
    def get_columns(self, tablename):
        return []

def text(sql):
    return sql

def joinedload(*args):
    return args

def relationship(*args, **kwargs):
    return property(lambda self: None)

# Datatypes
def DatatypeFactory(*args, **kwargs): return args

Integer = DatatypeFactory
String = DatatypeFactory
Boolean = DatatypeFactory
Text = DatatypeFactory
DateTime = DatatypeFactory
LargeBinary = DatatypeFactory
JSON = DatatypeFactory
def Enum(*args, **kwargs): return args
def ForeignKey(*args, **kwargs): return args
def Index(*args, **kwargs): return args

class FakeModelInstance:
    def __init__(self, data_dict, model_class, session=None):
        self._session = session
        self._collection_name = model_class.__tablename__
        self._model_class = model_class
        for k, v in data_dict.items():
            if k == "_id":
                continue # ignore mongo ID mapping
            setattr(self, k, v)
        # Apply defaults for any missing attributes attached to the model class
        for k in dir(model_class):
            if not k.startswith("_"):
                attr = getattr(model_class, k)
                if isinstance(attr, Column):
                    if not hasattr(self, k):
                        if attr.default is not None:
                            val = attr.default() if callable(attr.default) else attr.default
                            setattr(self, k, val)
                        else:
                            setattr(self, k, None)
                            
    def dict(self):
        d = {}
        for k in dir(self):
            if not k.startswith("_") and not callable(getattr(self, k)):
                d[k] = getattr(self, k)
        d.pop("metadata", None)
        return d
        
    def __getattr__(self, name):
        if name == "__tablename__":
            return self._collection_name
            
        # Handle @property attributes on the model class (e.g., is_sub_admin)
        attr = getattr(self._model_class, name, None)
        if isinstance(attr, property):
            try:
                val = attr.fget(self)
                if val is not None:
                    return val
            except Exception:
                pass

        # Handle relationships like "questions" based on the parent instance
        if not self._session:
            return [] if name.endswith("s") else None
            
        try:
            # If it's a property, try to fetch related docs
            # Simple heuristic: contests have questions, courses have papers
            if name == "questions":
                docs = self._session.db["contest_questions"].find({"contest_id": self.id})
                from main import ContestQuestion
                return [FakeModelInstance(doc, ContestQuestion, self._session) for doc in docs]
            if name == "papers":
                docs = self._session.db["papers"].find({"course_id": self.id})
                from main import Paper
                return [FakeModelInstance(doc, Paper, self._session) for doc in docs]
            
        except Exception:
            pass
            
        if name.endswith("s"):
            return []
        return None

class Query:
    def __init__(self, session, model):
        self.session = session
        self.model = model
        self.collection = session.db[model.__tablename__]
        self.query_filter = {}
        self._limit = 0
        self._offset = 0
        self._sort = None

    def _parse_condition(self, cond):
        if isinstance(cond, dict): # or_ / and_
            parsed_cond = {}
            for k, conditions_list in cond.items():
                parsed_cond[k] = [self._parse_condition(c) for c in conditions_list]
            return parsed_cond
            
        field_name = None
        for k in dir(self.model):
            if getattr(self.model, k) is cond.field:
                field_name = k
                break
        if not field_name:
            field_name = "unknown"

        if cond.op == "==":
            return {field_name: cond.val}
        elif cond.op == "!=":
            return {field_name: {"$ne": cond.val}}
        elif cond.op == "in":
            return {field_name: {"$in": cond.val}}
        elif cond.op == "ilike":
            import re
            pattern = cond.val.replace('%', '.*')
            return {field_name: {"$regex": pattern, "$options": "i"}}
        elif cond.op == ">":
             return {field_name: {"$gt": cond.val}}
        elif cond.op == ">=":
             return {field_name: {"$gte": cond.val}}
        elif cond.op == "<":
             return {field_name: {"$lt": cond.val}}
        elif cond.op == "<=":
             return {field_name: {"$lte": cond.val}}
        elif cond.op == "isnot":
             return {field_name: {"$ne": cond.val}}
        elif cond.op == "is":
             return {field_name: cond.val}
        return {}

    def filter(self, *conditions):
        for cond in conditions:
            parsed = self._parse_condition(cond)
            # Merge into query_filter safely using top level $and if necessary to prevent key overwrite
            if not self.query_filter:
                self.query_filter = parsed
            else:
                if "$and" not in self.query_filter:
                    self.query_filter = {"$and": [self.query_filter, parsed]}
                else:
                    self.query_filter["$and"].append(parsed)
        return self
        
    def order_by(self, *args):
        sort_fields = []
        for arg in args:
            if isinstance(arg, tuple): # func.desc() hack returned tuple earlier
                col, direction = arg
                # find col name
                name = [k for k in dir(self.model) if getattr(self.model, k) is col][0]
                sort_fields.append((name, direction))
            else:
                name = [k for k in dir(self.model) if getattr(self.model, k) is arg][0]
                sort_fields.append((name, 1))
        self._sort = sort_fields
        return self

    def offset(self, num):
        self._offset = num
        return self
        
    def limit(self, num):
        self._limit = num
        return self

    def first(self):
        cursor = self.collection.find(self.query_filter)
        if self._sort: cursor = cursor.sort(self._sort)
        if self._offset: cursor = cursor.skip(self._offset)
        doc = cursor.limit(1)
        res = list(doc)
        if res:
            obj = FakeModelInstance(res[0], self.model, self.session)
            if obj not in self.session._new_objects:
                self.session._new_objects.append(obj)
            return obj
        return None

    def all(self):
        cursor = self.collection.find(self.query_filter)
        if self._sort: cursor = cursor.sort(self._sort)
        if self._offset: cursor = cursor.skip(self._offset)
        if self._limit: cursor = cursor.limit(self._limit)
        results = [FakeModelInstance(doc, self.model, self.session) for doc in cursor]
        for obj in results:
            if obj not in self.session._new_objects:
                self.session._new_objects.append(obj)
        return results

    def count(self):
        return self.collection.count_documents(self.query_filter)
        
    def delete(self):
        self.session._scheduled_deletes.append((self.collection, self.query_filter))

    def options(self, *args):
        return self

class Session:
    def __init__(self, db):
        self.db = db
        self._new_objects = []
        self._scheduled_deletes = []

    def query(self, model):
        # We also need to hack class attributes to ensure Column identities hook up correctly 
        # Since SQLAlchemy models define fields like email = Column(String), 
        # mapping them is trivial via introspsction.
        return Query(self, model)

    def add(self, instance):
        self._new_objects.append(instance)

    def flush(self):
        # Assign IDs to new objects that don't have them yet
        # This is critical for dependencies (e.g., questions needing contest_id)
        table_max_ids = {}
        for inst in self._new_objects:
            table_name = inst.__tablename__
            if getattr(inst, "id", None) is None:
                if table_name not in table_max_ids:
                    collection = self.db[table_name]
                    max_doc = collection.find().sort("id", -1).limit(1)
                    curr_max = 0
                    for d in max_doc:
                        if d.get("id"): curr_max = int(d["id"])
                    
                    # Also check if any objects in the session already have a higher ID assigned manually
                    for other in self._new_objects:
                        if other.__tablename__ == table_name:
                            other_id = getattr(other, "id", None)
                            if other_id is not None:
                                curr_max = max(curr_max, int(other_id))
                    table_max_ids[table_name] = curr_max
                
                table_max_ids[table_name] += 1
                inst.id = table_max_ids[table_name]

    def commit(self):
        # 1. Execute scheduled deletes first
        for collection, query_filter in self._scheduled_deletes:
            collection.delete_many(query_filter)
        self._scheduled_deletes = []

        # 2. Ensure all objects have IDs (flush)
        self.flush()

        # 3. Execute scheduled upserts
        for inst in self._new_objects:
            collection = self.db[inst.__tablename__]
            doc = inst.dict()
            
            # Upsert
            collection.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)
        self._new_objects = []

    def refresh(self, instance):
        # Already set by commit logic, but simulating re-fetch
        collection = self.db[instance.__tablename__]
        doc = collection.find_one({"id": instance.id})
        if doc:
            for k, v in doc.items():
                if k != "_id":
                    setattr(instance, k, v)

    def close(self):
        pass

    def delete(self, instance):
        collection = self.db[instance.__tablename__]
        collection.delete_one({"id": getattr(instance, 'id')})
        self.commit()

class create_engine:
    def __init__(self, url, *args, **kwargs):
        self.client = MongoClient(url)
        # Ensure we connect to paperportal DB
        # if url string contains ?appName=paperportal, pymongo connects fine
        self.db = self.client.get_database("paperportal")
        
    def connect(self):
        class DummyConn:
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def execute(self, *a): return True
        return DummyConn()
        
    @property
    def dialect(self):
        class DummyDialect: name="postgresql"
        return DummyDialect()
        
    def begin(self):
         class DummyConn:
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def execute(self, *a): return True
         return DummyConn()

def sessionmaker(*args, **kwargs):
    bind = kwargs.get("bind")
    def maker():
        return Session(bind.db)
    return maker

