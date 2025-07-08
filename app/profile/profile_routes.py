from datetime import datetime
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, current_app
from bson import ObjectId
from bson.errors import InvalidId
from app.models.user import User
from app.auth.decorators import login_required
from app.profile.profile_forms import (
    ProfileUpdateForm, ChangePasswordForm, ProfileSettingsForm, 
    DeleteAccountForm, ProfilePictureForm, ContactInfoForm, 
    NotificationPreferencesForm
)
from flask_login import current_user
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

profile_bp = Blueprint("profile", __name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads', 'profiles')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route("/profile")
@login_required
def view_profile():
    """Display user's profile page."""
    db = current_app.db
    user_id = session.get("user_id")
    
    try:
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if not user_data:
            flash("User not found.", "danger")
            return redirect(url_for("auth.login"))
        
        # Get user statistics
        reports_count = db.reports.count_documents({'reported_by': ObjectId(user_id)})
        approved_reports = db.reports.count_documents({
            'reported_by': ObjectId(user_id),
            'status': 'Approved'
        })
        
        # Calculate reputation score
        reputation_score = min(100, (approved_reports * 10) + (reports_count * 5))
        
        user_stats = {
            'reports_count': reports_count,
            'approved_reports': approved_reports,
            'reputation_score': reputation_score
        }
        
        return render_template("profile/view.html", user=user_data, stats=user_stats)
        
    except InvalidId:
        flash("Invalid user ID.", "danger")
        return redirect(url_for("auth.login"))

@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Edit user's profile information."""
    db = current_app.db
    user_id = session.get("user_id")
    
    try:
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if not user_data:
            flash("User not found.", "danger")
            return redirect(url_for("auth.login"))
        
        form = ProfileUpdateForm(data=user_data)
        
        if form.validate_on_submit():
            update_data = {
                "first_name": form.first_name.data,
                "last_name": form.last_name.data,
                "display_name": form.display_name.data,
                "email": form.email.data,
                "phone": form.phone.data,
                "bio": form.bio.data,
                "location": form.location.data,
                "updated_at": datetime.utcnow()
            }
            
            # Handle profile picture upload
            if form.avatar.data:
                avatar = form.avatar.data
                if allowed_file(avatar.filename):
                    # Create upload directory if it doesn't exist
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    
                    filename = secure_filename(avatar.filename)
                    unique_filename = f"{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                    avatar.save(os.path.join(UPLOAD_FOLDER, unique_filename))
                    update_data["avatar"] = f"/static/uploads/profiles/{unique_filename}"
                else:
                    flash("Invalid file type. Please upload JPG, JPEG, PNG, or GIF files only.", "danger")
                    return render_template("profile/edit.html", form=form)
            
            # Update user in database
            db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile.view_profile"))
        
        return render_template("profile/edit.html", form=form)
        
    except InvalidId:
        flash("Invalid user ID.", "danger")
        return redirect(url_for("auth.login"))

@profile_bp.route("/profile/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change user's password."""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        db = current_app.db
        user_id = session.get("user_id")
        
        # Generate new password hash
        new_password_hash = generate_password_hash(
            form.new_password.data, 
            method='pbkdf2:sha256', 
            salt_length=16
        )
        
        # Update password in database
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": new_password_hash, "updated_at": datetime.utcnow()}}
        )
        
        flash("Password changed successfully!", "success")
        return redirect(url_for("profile.view_profile"))
    
    return render_template("profile/change_password.html", form=form)

@profile_bp.route("/profile/settings", methods=["GET", "POST"])
@login_required
def profile_settings():
    """Manage profile settings and preferences."""
    db = current_app.db
    user_id = session.get("user_id")
    
    try:
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if not user_data:
            flash("User not found.", "danger")
            return redirect(url_for("auth.login"))
        
        # Get current settings or set defaults
        current_settings = user_data.get('settings', {})
        form = ProfileSettingsForm(data=current_settings)
        
        if form.validate_on_submit():
            settings_data = {
                "settings.email_notifications": form.email_notifications.data,
                "settings.privacy_level": form.privacy_level.data,
                "settings.location_sharing": form.location_sharing.data,
                "settings.language": form.language.data,
                "updated_at": datetime.utcnow()
            }
            
            db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": settings_data}
            )
            
            flash("Settings updated successfully!", "success")
            return redirect(url_for("profile.profile_settings"))
        
        return render_template("profile/settings.html", form=form)
        
    except InvalidId:
        flash("Invalid user ID.", "danger")
        return redirect(url_for("auth.login"))

@profile_bp.route("/profile/upload-picture", methods=["GET", "POST"])
@login_required
def upload_picture():
    """Upload profile picture."""
    form = ProfilePictureForm()
    
    if form.validate_on_submit():
        db = current_app.db
        user_id = session.get("user_id")
        
        avatar = form.avatar.data
        if allowed_file(avatar.filename):
            # Create upload directory if it doesn't exist
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            filename = secure_filename(avatar.filename)
            unique_filename = f"{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
            avatar.save(os.path.join(UPLOAD_FOLDER, unique_filename))
            
            avatar_url = f"/static/uploads/profiles/{unique_filename}"
            
            # Update user's avatar in database
            db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"avatar": avatar_url, "updated_at": datetime.utcnow()}}
            )
            
            flash("Profile picture uploaded successfully!", "success")
            return redirect(url_for("profile.view_profile"))
        else:
            flash("Invalid file type. Please upload JPG, JPEG, PNG, or GIF files only.", "danger")
    
    return render_template("profile/upload_picture.html", form=form)

@profile_bp.route("/profile/contact-info", methods=["GET", "POST"])
@login_required
def contact_info():
    """Manage contact information."""
    db = current_app.db
    user_id = session.get("user_id")
    
    try:
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if not user_data:
            flash("User not found.", "danger")
            return redirect(url_for("auth.login"))
        
        form = ContactInfoForm(data=user_data)
        
        if form.validate_on_submit():
            contact_data = {
                "phone": form.phone.data,
                "address": form.address.data,
                "website": form.website.data,
                "social_media": form.social_media.data,
                "updated_at": datetime.utcnow()
            }
            
            db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": contact_data}
            )
            
            flash("Contact information updated successfully!", "success")
            return redirect(url_for("profile.view_profile"))
        
        return render_template("profile/contact_info.html", form=form)
        
    except InvalidId:
        flash("Invalid user ID.", "danger")
        return redirect(url_for("auth.login"))

@profile_bp.route("/profile/notifications", methods=["GET", "POST"])
@login_required
def notification_preferences():
    """Manage notification preferences."""
    db = current_app.db
    user_id = session.get("user_id")
    
    try:
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if not user_data:
            flash("User not found.", "danger")
            return redirect(url_for("auth.login"))
        
        # Get current notification preferences or set defaults
        current_prefs = user_data.get('notification_preferences', {})
        form = NotificationPreferencesForm(data=current_prefs)
        
        if form.validate_on_submit():
            prefs_data = {
                "notification_preferences.email_reports": form.email_reports.data,
                "notification_preferences.email_alerts": form.email_alerts.data,
                "notification_preferences.sms_alerts": form.sms_alerts.data,
                "notification_preferences.push_notifications": form.push_notifications.data,
                "updated_at": datetime.utcnow()
            }
            
            db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": prefs_data}
            )
            
            flash("Notification preferences updated successfully!", "success")
            return redirect(url_for("profile.notification_preferences"))
        
        return render_template("profile/notifications.html", form=form)
        
    except InvalidId:
        flash("Invalid user ID.", "danger")
        return redirect(url_for("auth.login"))

@profile_bp.route("/profile/delete-account", methods=["GET", "POST"])
@login_required
def delete_account():
    """Delete user account."""
    form = DeleteAccountForm()
    
    if form.validate_on_submit():
        db = current_app.db
        user_id = session.get("user_id")
        
        # Soft delete - mark as deleted instead of removing
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"deleted": True, "deleted_at": datetime.utcnow()}}
        )
        
        # Clear session
        session.clear()
        
        flash("Your account has been deleted successfully.", "info")
        return redirect(url_for("auth.login"))
    
    return render_template("profile/delete_account.html", form=form)

@profile_bp.route("/profile/activity")
@login_required
def activity_log():
    """Display user's activity log."""
    db = current_app.db
    user_id = session.get("user_id")
    
    try:
        # Get user's recent reports
        recent_reports = list(db.reports.find(
            {'reported_by': ObjectId(user_id)},
            sort=[('date_reported', -1)],
            limit=20
        ))
        
        # Format activity data
        activities = []
        for report in recent_reports:
            activities.append({
                'type': 'report_created',
                'title': f"Created report: {report['title']}",
                'date': report.get('date_reported', datetime.utcnow()),
                'status': report.get('status', 'Pending'),
                'report_id': str(report['_id'])
            })
        
        return render_template("profile/activity.html", activities=activities)
        
    except InvalidId:
        flash("Invalid user ID.", "danger")
        return redirect(url_for("auth.login"))
