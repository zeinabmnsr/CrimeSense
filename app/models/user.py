from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from flask_login import UserMixin 
from datetime import datetime 
import re 

class User(UserMixin):
    def __init__(self, user_dict):
        self._id = user_dict["_id"]  # Store the raw ObjectId
        self.id = str(self._id)      # Keep string version for Flask-Login
        self.email = user_dict["email"]
        self.password_hash = user_dict["password"]
        self.first_name = user_dict.get("first_name", "")
        self.last_name = user_dict.get("last_name", "")

    @classmethod
    def create(cls, first_name, last_name, email, password, db):
        if not User.validate_password(password):
            raise ValueError("Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character")
        if not User.validate_email(email):
            raise ValueError("Invalid email format")
        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        user = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email.lower(),
                'password': password_hash,
                'role': 'user' ,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
                }
        inserted_user = db.users.insert_one(user)
        return inserted_user.inserted_id  # Return user ID
    
    @staticmethod
    def create_admin(first_name, last_name, email, password, role, db, is_super_admin=False):
        """Create a new admin user"""
        if not User.validate_password(password):
            raise ValueError("Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character")
        if not User.validate_email(email):
            raise ValueError("Invalid email format")
        
        hashed_password = generate_password_hash(password)
        
        user_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email.lower(),
            'password': hashed_password,
            'role': role,
            'is_super_admin': is_super_admin,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.users.insert_one(user_data)
        return result.inserted_id

    def find_by_email(email, db):
        """Find user by email"""
        return db.users.find_one({'email': email.lower()})

    @staticmethod
    def find_by_id(user_id, db):
        """Find user by ID"""
        return db.users.find_one({'_id': ObjectId(user_id)})
    #hlmethod bs bda trj3lna user data like name

    @staticmethod
    def verify_password(stored_hash, password):
        return check_password_hash(stored_hash, password)

    @staticmethod
    def get_user_profile(user_id, db):
        """Get user profile without password"""
        user = db.users.find_one({'_id': ObjectId(user_id)}, {'password': 0})
        if user:
            user['_id'] = str(user['_id'])
        return user
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    @staticmethod
    def update_profile(user_id, data, db):
        """Update user profile"""
        data['updated_at'] = datetime.utcnow()
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': data}
        )
        return result.modified_count > 0