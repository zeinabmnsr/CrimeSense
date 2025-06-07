from datetime import datetime
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, current_app
from bson import ObjectId
from bson.errors import InvalidId
from app.models import reports
from app.models.reports import CrimeReport
from app.models.user import User
from app.auth.decorators import login_required
from app.crime_reports.reports_forms import CrimeReportForm
from flask_login import current_user
import os
from werkzeug.utils import secure_filename

reports_bp = Blueprint("reports", __name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

@reports_bp.route("/reports", methods=["GET"])
@login_required
def list_reports():
    """Show all crime reports"""
    db = current_app.db
    reports = CrimeReport.get_all_reports(db)
    
    for report in reports:
        reporter = db.users.find_one({"_id": report["reported_by"]})
        report["reported_name"] = f"{reporter.get('first_name', '')} {reporter.get('last_name', '')}" if reporter else "Unknown"
    
    return render_template("reports/list.html", reports=reports)

@reports_bp.route("/reports/create", methods=["GET", "POST"])
@login_required
def create_report():
    """Admin creates a new crime report"""
    form = CrimeReportForm()
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            image = form.image.data
            filename = secure_filename(image.filename)
            image_filename = datetime.utcnow().strftime("%Y%m%d%H%M%S_") + filename
            image.save(os.path.join(UPLOAD_FOLDER, image_filename))

        report_data = {
            "title": form.title.data,
            "description": form.description.data,
            "location": form.location.data,
            "crime_type": form.crime_type.data,
            "date_occured": datetime.combine(form.date_occured.data, datetime.min.time()),
            "date_reported": datetime.utcnow(),
            "is_public": form.is_public.data,
            "status": form.status.data,
            "reported_by": ObjectId(current_user.get_id()),
            "image_path": image_filename
        }

        db = current_app.db
        CrimeReport.created_report(report_data, db)
        flash("Crime report created successfully!", "success")
        return redirect(url_for("reports.list_reports"))

    return render_template("reports/create.html", form=form)

@reports_bp.route("/reports/edit/<report_id>", methods=["GET", "POST"])
@login_required
def edit_report(report_id):
    """Admin edits an existing crime report"""
    db = current_app.db
    try:
        report = CrimeReport.get_report_by_id(report_id, db)
    except InvalidId:
        flash("Invalid report ID.", "danger")
        return redirect(url_for("reports.list_reports"))
    
    if not report:
        flash("Report not found.", "danger")
        return redirect(url_for("reports.list_reports"))

    if str(report["reported_by"]) != current_user.get_id():
        flash("You can only edit reports you submitted.", "danger")
        return redirect(url_for("reports.list_reports"))

    form = CrimeReportForm(data=report)

    if form.validate_on_submit():
        updated_data = {
            "title": form.title.data,
            "description": form.description.data,
            "location": form.location.data,
            "crime_type": form.crime_type.data,
            "is_public": form.is_public.data,
            "status": form.status.data
        }

        if form.image.data:
            image = form.image.data
            filename = secure_filename(image.filename)
            image_filename = datetime.utcnow().strftime("%Y%m%d%H%M%S_") + filename
            image.save(os.path.join(UPLOAD_FOLDER, image_filename))
            updated_data["image_path"] = image_filename

        CrimeReport.update_report(report_id, updated_data, db)
        flash("Crime report updated successfully!", "success")
        return redirect(url_for("reports.list_reports"))

    return render_template("reports/edit.html", form=form, report_id=report_id)

@reports_bp.route("/reports/delete/<report_id>", methods=["POST"])
@login_required
def delete_report(report_id):
    """Admin deletes a crime report"""
    db = current_app.db
    try:
        report = CrimeReport.get_report_by_id(report_id, db)
    except InvalidId:
        flash("Invalid report ID.", "danger")
        return redirect(url_for("reports.list_reports"))

    if not report:
        flash("Report not found.", "danger")
        return redirect(url_for("reports.list_reports"))

    if str(report["reported_by"]) != current_user.get_id():
        flash("You can only delete reports you submitted.", "danger")
        return redirect(url_for("reports.list_reports"))

    CrimeReport.delete_report(report_id, db)
    flash("Crime report deleted successfully!", "success")
    return redirect(url_for("reports.list_reports"))
