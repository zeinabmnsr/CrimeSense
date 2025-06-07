from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from app.models.reports import CrimeReport
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from datetime import datetime

reports_api_bp = Blueprint("reports_api", __name__, url_prefix="/api/reports")

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@reports_api_bp.route("/create", methods=['POST'])
@jwt_required()
def create_report():
    """Allows a mobile user to create a new crime report."""
    data = request.form.to_dict()
    db = current_app.db
    current_user_id = get_jwt_identity()

    if 'image' in request.files:
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_filename = datetime.utcnow().strftime("%Y%m%d%H%M%S_") + filename
            image.save(os.path.join(UPLOAD_FOLDER, image_filename))
            data['image_path'] = image_filename
        else:
            return jsonify({"error": "Invalid image file"}), 400

    report_data = {
        "title": data.get("title"),
        "description": data.get("description"),
        "location": data.get("location"),
        "crime_type": data.get("crime_type"),
        "date_occured": datetime.fromisoformat(data["date_occured"]) if data.get("date_occured") else datetime.utcnow(),
        "reported_by": ObjectId(current_user_id),
        "is_public": False, # Defaults to False for mobile reports
        "status": "Pending", # Defaults to Pending
        "image_path": data.get("image_path")
    }

    # Validate required fields
    required_fields = ["title", "description", "location", "crime_type", "date_occured"]
    for field in required_fields:
        if not report_data[field]:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    report_id = CrimeReport.created_report(report_data, db)
    return jsonify({"message": "Report created successfully", "report_id": str(report_id)}), 201

@reports_api_bp.route("/my-reports", methods=['GET'])
@jwt_required()
def get_my_reports():
    """Fetches all reports submitted by the current user."""
    db = current_app.db
    current_user_id = get_jwt_identity()
    
    reports = CrimeReport.get_all_reports(db, filters={"reported_by": ObjectId(current_user_id)})
    
    # Convert ObjectId to string for JSON serialization
    for report in reports:
        report['_id'] = str(report['_id'])
        report['reported_by'] = str(report['reported_by'])

    return jsonify(reports), 200

@reports_api_bp.route("/", methods=['GET'])
@jwt_required()
def get_public_reports():
    """Fetches all public reports, with optional filtering."""
    db = current_app.db
    
    # Start with a base filter for public reports
    filters = {"is_public": True}
    
    # Add optional query parameters for filtering
    if 'crime_type' in request.args:
        filters['crime_type'] = request.args['crime_type']
    if 'location' in request.args:
        # Using regex for partial matching on location
        filters['location'] = {"$regex": request.args['location'], "$options": "i"}
    if 'date' in request.args:
        try:
            # Assuming date is passed in YYYY-MM-DD format
            search_date = datetime.strptime(request.args['date'], "%Y-%m-%d")
            # Create a date range for the entire day
            start_of_day = datetime(search_date.year, search_date.month, search_date.day)
            end_of_day = datetime(search_date.year, search_date.month, search_date.day, 23, 59, 59)
            filters['date_occured'] = {"$gte": start_of_day, "$lte": end_of_day}
        except ValueError:
            return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    reports = CrimeReport.get_all_reports(db, filters=filters)
    
    # Convert ObjectId to string for JSON serialization
    for report in reports:
        report['_id'] = str(report['_id'])
        report['reported_by'] = str(report['reported_by'])

    return jsonify(reports), 200