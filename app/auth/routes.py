from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.auth.forms import RegisterForm, LoginForm
from app.models.user import User
from app.auth.decorators import login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Blueprint for web-based (session) authentication
auth_bp = Blueprint('auth', __name__)

# Blueprint for API-based (JWT) authentication
auth_api_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')

limiter = Limiter(get_remote_address, default_limits=["10 per minute"])

# --- Web Routes (Session-Based) ---

@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data

        db = current_app.db
        if User.find_by_email(email, db):
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        User.create(first_name, last_name, email, password, db)
        flash('Registration successful!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password_input = form.password.data

        db = current_app.db
        user = User.find_by_email(email, db)
        if user and User.verify_password(user['password'], password_input):
            session['user_id'] = str(user['_id'])
            flash('Login successful!', 'success')
            return redirect(url_for('auth.home'))
######zabte el redirect hon
        flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)

@auth_bp.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template("dashboard.html", user=session['user'])
    return redirect(url_for('auth.login'))

@auth_bp.route('/home')
@login_required
def home():
    db = current_app.db
    user = db.users.find_one({"_id": ObjectId(session['user_id'])})
    
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("home.html", 
                           first_name=user.get("first_name", ""),
                           last_name=user.get("last_name", ""))

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    flash('You have been logged out. ', 'success')
    return redirect(url_for('auth.login'))

# --- API Routes (JWT-Based) ---

@auth_api_bp.route('/register', methods=['POST'])
def api_register():
    data = request.json

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")

    db = current_app.db
    if User.find_by_email(email, db):
        return jsonify({"error": "Email already registered"}), 400
    user_id = User.create(first_name, last_name, email, password, db)

    return jsonify({"message": "User registered successfully", "user_id": str(user_id)}), 201

@auth_api_bp.route('/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get("email")
    password_input = data.get("password")

    db = current_app.db
    user = User.find_by_email(email, db)

    if user and User.verify_password(user['password'], password_input):
        access_token = create_access_token(identity=str(user["_id"]))
        return jsonify({"message": "Login successful", "access_token": access_token}), 200
    return jsonify({"error": "Invalid email or password"}), 401

@auth_api_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected_route():
    current_user_id = get_jwt_identity()
    return jsonify({"message": "Welcome!", "user_id": current_user_id}), 200