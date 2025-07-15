from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.auth.forms import RegisterForm, LoginForm, AdminRegisterForm
from app.models.user import User
from app.auth.decorators import login_required, admin_required, super_admin_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Blueprint for web-based (session) authentication
auth_bp = Blueprint('auth', __name__)

# Blueprint for API-based (JWT) authentication
auth_api_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')

limiter = Limiter(get_remote_address, default_limits=["10 per minute"])

# --- Web Routes (Session-Based) ---

@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
@super_admin_required
@limiter.limit("10 per minute")
def register():
    form = AdminRegisterForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        role = form.role.data 
        is_super_admin = form.is_super_admin.data

        db = current_app.db

        if User.find_by_email(email, db):
            flash('Email already registered.', 'danger')
            return render_template('auth/admin_register.html', form=form)

        try:
            # Create admin user
            user_id = User.create_admin(first_name, last_name, email, password, role, db, is_super_admin)
            flash(f'Admin user created successfully! Email: {email}', 'success')
            return redirect(url_for('auth.register'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'danger')
            print(f"Admin registration error: {e}")
    
    return render_template('auth/admin_register.html', form=form)

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
            if user.get('role') != 'admin':
                flash('Access denied. Admin credentials required.', 'danger')
                return render_template('auth/login.html', form=form)
            
            session['user_id'] = str(user['_id'])
            session['user_name'] = f"{user['first_name']} {user['last_name']}"
            session['user_role'] = user.get('role', 'user')
            session['is_super_admin'] = user.get('is_super_admin', False)
            flash('Login successful!', 'success')
            return redirect(url_for('auth.dashboard'))
        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/dashboard')
@admin_required
@login_required
def dashboard():
    db = current_app.db
    user = User.get_user_profile(session['user_id'], db)
    # Get statistics for admin dashboard
    stats = {
        'total_users': db.users.count_documents({}),
        'total_admins': db.users.count_documents({'role': 'admin'}),
        'total_reports': db.reports.count_documents({}) if 'reports' in db.list_collection_names() else 0,
        'total_hotspots': db.hotspots.count_documents({}) if 'hotspots' in db.list_collection_names() else 0,
        'total_contacts': db.contacts.count_documents({}) if 'contacts' in db.list_collection_names() else 0,
        'pending_reports': db.reports.count_documents({'status': 'Pending'}) if 'reports' in db.list_collection_names() else 0
    }
    return render_template("auth/admin_dashboard.html", user=user, stats=stats, first_name=user.get("first_name", ""),
                           last_name=user.get("last_name", ""))

@auth_bp.route('/profile')
@admin_required
def profile():
    db = current_app.db
    user = User.get_user_profile(session['user_id'], db)
    #zbte lpath ll profile.html
    return render_template("auth/profile.html", user=user)

@auth_bp.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    session.pop('user_id', None)
    flash('You have been logged out. ', 'success')
    return redirect(url_for('home'))

@auth_bp.route('/admin/users')
@admin_required
def admin_users():
    """View all users (admin only)"""
    db = current_app.db
    users = list(db.users.find({}, {'password': 0}).sort('created_at', -1))
    
    for user in users:
        user['_id'] = str(user['_id'])
    
    return render_template('auth/admin_users.html', users=users)

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


@auth_api_bp.route('/profile', methods=['GET'])
@jwt_required()
def api_profile():
    current_user_id = get_jwt_identity()
    db = current_app.db
    user = User.get_user_profile(current_user_id, db)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user}), 200

'''
This is a test route for verification, that the mobile
 user has a valid JWT. You can hit this after 
login to confirm authentication is working.
You can:
Keep it for testing
Or delete it later if you don't use it
'''
@auth_api_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected_route():
    current_user_id = get_jwt_identity()
    return jsonify({"message": "helloooooo", "user_id": current_user_id}), 200