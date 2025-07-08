from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from datetime import datetime

profile_api_bp = Blueprint("profile_api", __name__, url_prefix="/api/users")

UPLOAD_FOLDER = os.path.join('static', 'uploads', 'profiles')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_api_bp.route("/profile", methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile information."""
    db = current_app.db
    current_user_id = get_jwt_identity()
    
    try:
        user_data = db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user_data:
            return jsonify({"error": "User not found"}), 404
        
        # Remove sensitive information
        user_data.pop('password', None)
        user_data['_id'] = str(user_data['_id'])
        
        # Add computed fields
        user_data['display_name'] = user_data.get('display_name') or f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        user_data['username'] = user_data.get('username') or user_data.get('email', '').split('@')[0]
        
        return jsonify(user_data), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch profile"}), 500

@profile_api_bp.route("/profile", methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile information."""
    db = current_app.db
    current_user_id = get_jwt_identity()
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    try:
        # Validate user exists
        user_data = db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user_data:
            return jsonify({"error": "User not found"}), 404
        
        # Prepare update data
        update_data = {}
        
        # Allow updating specific fields
        allowed_fields = ['first_name', 'last_name', 'display_name', 'bio', 'phone', 'location']
        for field in allowed_fields:
            if field in data and data[field] is not None:
                update_data[field] = data[field]
        
        # Add updated timestamp
        update_data['updated_at'] = datetime.utcnow()
        
        # Update user in database
        result = db.users.update_one(
            {'_id': ObjectId(current_user_id)},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            return jsonify({"message": "Profile updated successfully"}), 200
        else:
            return jsonify({"message": "No changes made"}), 200
            
    except Exception as e:
        return jsonify({"error": "Failed to update profile"}), 500

@profile_api_bp.route("/upload-profile-pic", methods=['POST'])
@jwt_required()
def upload_profile_picture():
    """Upload and update user's profile picture."""
    db = current_app.db
    current_user_id = get_jwt_identity()
    
    if 'avatar' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Create upload directory if it doesn't exist
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{current_user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Update user's avatar in database
            avatar_url = f"/static/uploads/profiles/{unique_filename}"
            result = db.users.update_one(
                {'_id': ObjectId(current_user_id)},
                {'$set': {'avatar': avatar_url, 'updated_at': datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                return jsonify({
                    "message": "Profile picture uploaded successfully",
                    "avatar_url": avatar_url
                }), 200
            else:
                return jsonify({"error": "Failed to update profile picture"}), 500
                
        except Exception as e:
            return jsonify({"error": "Failed to upload file"}), 500
    else:
        return jsonify({"error": "Invalid file type. Only JPG, JPEG, PNG, and GIF are allowed."}), 400

@profile_api_bp.route("/stats", methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user statistics (reports count, reputation, etc.)."""
    db = current_app.db
    current_user_id = get_jwt_identity()
    
    try:
        # Get reports count
        reports_count = db.reports.count_documents({'reported_by': ObjectId(current_user_id)})
        
        # Get approved reports count
        approved_reports = db.reports.count_documents({
            'reported_by': ObjectId(current_user_id),
            'status': 'Approved'
        })
        
        # Calculate basic reputation score (can be enhanced)
        reputation_score = min(100, (approved_reports * 10) + (reports_count * 5))
        
        # Determine badge based on reputation
        if reputation_score >= 90:
            badge = "Elite Reporter"
        elif reputation_score >= 70:
            badge = "Verified Reporter"
        elif reputation_score >= 50:
            badge = "Trusted Citizen"
        elif reputation_score >= 30:
            badge = "Active Reporter"
        elif reputation_score >= 10:
            badge = "Observer"
        else:
            badge = "New User"
        
        stats = {
            "reports_count": reports_count,
            "approved_reports": approved_reports,
            "reputation_score": reputation_score,
            "badge": badge,
            "join_date": db.users.find_one({'_id': ObjectId(current_user_id)}).get('created_at', datetime.utcnow()).isoformat()
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch user statistics"}), 500

@profile_api_bp.route("/reputation", methods=['GET'])
@jwt_required()
def get_reputation():
    """Get detailed reputation information."""
    db = current_app.db
    current_user_id = get_jwt_identity()
    
    try:
        # Get user reports
        reports = list(db.reports.find({'reported_by': ObjectId(current_user_id)}))
        
        total_reports = len(reports)
        verified_reports = len([r for r in reports if r.get('status') == 'Approved'])
        helpful_votes = sum([r.get('helpful_votes', 0) for r in reports])
        
        # Calculate reputation score
        score = min(100, (verified_reports * 15) + (helpful_votes * 5) + (total_reports * 2))
        
        reputation_data = {
            "score": score,
            "total_reports": total_reports,
            "verified_reports": verified_reports,
            "helpful_votes": helpful_votes
        }
        
        return jsonify(reputation_data), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch reputation data"}), 500

@profile_api_bp.route("/reputation/history", methods=['GET'])
@jwt_required()
def get_reputation_history():
    """Get reputation history/activity log."""
    db = current_app.db
    current_user_id = get_jwt_identity()
    
    try:
        # Get recent activities (this would be enhanced with a proper activity log)
        recent_reports = list(db.reports.find(
            {'reported_by': ObjectId(current_user_id)},
            sort=[('date_reported', -1)],
            limit=10
        ))
        
        history = []
        for report in recent_reports:
            if report.get('status') == 'Approved':
                history.append({
                    "id": str(report['_id']),
                    "action": "Crime Report Verified",
                    "points": 15,
                    "date": report.get('date_reported', datetime.utcnow()).strftime('%Y-%m-%d %H:%M'),
                    "type": "positive"
                })
            elif report.get('helpful_votes', 0) > 0:
                history.append({
                    "id": str(report['_id']),
                    "action": "Report Marked Helpful",
                    "points": report.get('helpful_votes', 0) * 5,
                    "date": report.get('date_reported', datetime.utcnow()).strftime('%Y-%m-%d %H:%M'),
                    "type": "positive"
                })
        
        return jsonify({"history": history}), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch reputation history"}), 500

@profile_api_bp.route("/change-password", methods=['POST'])
@jwt_required()
def change_password():
    """Change user's password."""
    db = current_app.db
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({"error": "Current password and new password are required"}), 400
    
    try:
        # Get user data
        user_data = db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user_data:
            return jsonify({"error": "User not found"}), 404
        
        # Verify current password
        if not User.verify_password(user_data['password'], data['current_password']):
            return jsonify({"error": "Current password is incorrect"}), 400
        
        # Generate new password hash
        from werkzeug.security import generate_password_hash
        new_password_hash = generate_password_hash(data['new_password'], method='pbkdf2:sha256', salt_length=16)
        
        # Update password
        result = db.users.update_one(
            {'_id': ObjectId(current_user_id)},
            {'$set': {'password': new_password_hash, 'updated_at': datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            return jsonify({"message": "Password changed successfully"}), 200
        else:
            return jsonify({"error": "Failed to change password"}), 500
            
    except Exception as e:
        return jsonify({"error": "Failed to change password"}), 500

@profile_api_bp.route("/delete-account", methods=['DELETE'])
@jwt_required()
def delete_account():
    """Delete user account (soft delete)."""
    db = current_app.db
    current_user_id = get_jwt_identity()
    
    try:
        # Soft delete - mark as deleted instead of removing
        result = db.users.update_one(
            {'_id': ObjectId(current_user_id)},
            {'$set': {'deleted': True, 'deleted_at': datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            return jsonify({"message": "Account deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete account"}), 500
            
    except Exception as e:
        return jsonify({"error": "Failed to delete account"}), 500
