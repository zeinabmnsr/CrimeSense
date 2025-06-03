from functools import wraps 
from flask import session, redirect, url_for, flash 
from bson import ObjectId 
from flask import current_app 

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

'''
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db= current_app.db 
        user = db.users.find_one({'_id': ObjetcId(session['user_id'])})
        
        if 'user_id' not in session:
            flash("Admin access required. ", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function
'''
