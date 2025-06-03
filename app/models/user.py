from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from flask_login import UserMixin 

class User(UserMixin):
    def __init__(self, user_dict):
        self.id = str(user_dict["_id"])
        self.email = user_dict["email"]
        self.password_hash = user_dict["password"]
        self.first_name = user_dict.get("first_name", "")
        self.last_name = user_dict.get("last_name", "")

    @classmethod
    def create(cls, first_name, last_name, email, password, db):
        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        user = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email, 
                'password': password_hash }
        inserted_user = db.users.insert_one(user)
        return inserted_user.inserted_id  # Return user ID

    @classmethod 
    def get_by_id(cls, user_id, db):
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return cls(user_data)
        return None

    '''
    @classmethod
    def find_by_id(cls, user_id, db):
        return db.users.find_one({'_id': ObjectId(user_id)})
    hlmethod bs bda trj3lna user data like name
    '''
    @classmethod
    def find_by_email(cls, email, db):
        return db.users.find_one({'email': email})

    @staticmethod
    def verify_password(stored_hash, password):
        return check_password_hash(stored_hash, password)
