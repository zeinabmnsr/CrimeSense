from flask import Flask, current_app
from pymongo import MongoClient
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_cors import CORS
from flask_limiter import Limiter 
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager
from flask_login import LoginManager 
from app.models.user import User 
from app.crime_parser.parse_crime_data import parse_and_insert

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
login_manager = LoginManager()
load_dotenv()
csrf = CSRFProtect()  

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config["ENV"] = "development"
    
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    jwt = JWTManager(app)

    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    csrf.init_app(app)
    login_manager.init_app(app) 
    login_manager.login_view = 'auth.login'

    @app.context_processor 
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf 
        return dict(csrf_token=generate_csrf)

    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    db = client.get_database() 
    app.db = db  
    
    #current_app.db["parsed_crimes"]

    limiter = Limiter(
        get_remote_address, 
        app = app,
        default_limits=["10 per minute"]
    )

    #csrf = CSRFProtect(app)
    CORS(app, supports_credentials=True)

    print("MONGO_URI:", mongo_uri)
    print("Connected Database:", db.name)

    from app.auth.routes import auth_bp, auth_api_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    csrf.exempt(auth_api_bp)

    app.register_blueprint(auth_api_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    from app.crime_reports.reports_routes import reports_bp
    app.register_blueprint(reports_bp)

    from app.crime_reports.reports_api_routes import reports_api_bp
    csrf.exempt(reports_api_bp)
    app.register_blueprint(reports_api_bp)

    from app.user_contacts.contacts_api_routes import contacts_api
    csrf.exempt(contacts_api)
    app.register_blueprint(contacts_api)


    return app