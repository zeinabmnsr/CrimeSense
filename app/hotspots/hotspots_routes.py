from datetime import datetime
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, current_app
from bson import ObjectId
from bson.errors import InvalidId
from app.models import reports
from app.models.hotspot import Hotspot
from app.models.user import User
from app.auth.decorators import login_required
from app.hotspots.hotspots_forms import DeleteHotspotForm, HotspotsForm
from flask_login import current_user
import os
from werkzeug.utils import secure_filename

hotspots_bp = Blueprint("hotspots", __name__) 

@hotspots_bp.route("/", methods=["GET"])
@login_required 
def list_hotspots():
    db = current_app.db 
    try:
        hotspots = Hotspot.get_all_hotspots(db)
        
        # Add sender information to each hotspot
        for hotspot in hotspots:
            sender = db.users.find_one({"_id": hotspot["created_by"]})
            hotspot["sender_name"] = f"{sender.get('first_name', '')} {sender.get('last_name', '')}" if sender else "Unknown"
        
        delete_form = DeleteHotspotForm()
        return render_template("hotspots/list_hotspots.html", hotspots=hotspots, form=delete_form)
    except Exception as e:
        flash("Error loading hotspots.", "danger")
        return redirect(url_for("auth.dashboard"))
    
@hotspots_bp.route("/create", methods=["GET", "POST"])
@login_required 
def create_hotspot():
    """Create a new hotspot"""
    form = HotspotsForm()
    if form.validate_on_submit():
        hotspot_data = {
            "crime_type": form.crime_type.data,
            "location" : form.location.data,
            "lat" : form.lat.data,
            "lng": form.lng.data,
            "danger_time": datetime.combine(form.danger_time.data, datetime.min.time()),
            "notes": form.notes.data,
            "created_at" : datetime.utcnow(),
            "created_by" : ObjectId(session.get("user_id"))
        }

        db = current_app.db 
        try:
            Hotspot.create_hotspot(hotspot_data, db)
            flash("Hotspot added successfully!", "success")
            return redirect(url_for("hotspots.list_hotspots"))
        except Exception as e:
            flash("Error creating hotspot. Please try again.", "danger")
    
    return render_template("hotspots/add_hotspots.html", form=form)

@hotspots_bp.route("/edit/<hotspot_id>", methods=["GET", "POST"])
@login_required 
def edit_hotspot(hotspot_id):
    db = current_app.db 
    try: 
        hotspot = Hotspot.get_hotspot_by_id(hotspot_id, db)
    except InvalidId:
        flash("Invalid hotspot ID.","danger")
        return redirect(url_for("hotspots.list_hotspots"))
    if not hotspot: 
        flash("Hotspot Not Found.", "danger")
        return redirect(url_for("hotspots.list_hotspots"))
    
    print("created_by in DB:", hotspot["created_by"]) #for testing
    print("current_user ID : ", session.get("user_id")) 

    if str(hotspot["created_by"]) != session.get("user_id"):
        flash("You can only edit hotspots you added.", "danger")
        return redirect(url_for("hotspots.list_hotspots"))
    form = HotspotsForm(data={
    "crime_type": hotspot["crime_type"],
    "location": hotspot["location"],
    "lat": str(hotspot.get("lat", "")),
    "lng": str(hotspot.get("lng", "")),
    "danger_time": hotspot.get("danger_time"),
    "notes": hotspot.get("notes", "")
})

    if form.validate_on_submit():
        updated_data = {
            "crime_type": form.crime_type.data,
            "notes": form.notes.data,
            "location": form.location.data,
            "lat" : form.lat.data,
            "lng" : form.lng.data,
            "danger_time": datetime.combine(form.danger_time.data, datetime.min.time())
        }

        try:
            Hotspot.update_hotspot(hotspot_id, updated_data, db)
            flash("Hotspot updated successfully!", "success")
            return redirect(url_for("hotspots.list_hotspots"))
        except Exception as e:
            flash("Error updating hotspot. Please try again.", "danger")
    
    return render_template("hotspots/edit_hotspots.html", form=form, hotspot_id=hotspot_id)

@hotspots_bp.route("/delete/<hotspot_id>", methods=["POST"])
@login_required
def delete_hotspot(hotspot_id):
    db = current_app.db
    try:
        hotspot = Hotspot.get_hotspot_by_id(hotspot_id, db)
    except InvalidId:
        flash("Invalid hotspot ID.", "danger")
        return redirect(url_for("hotspots.list_hotspots"))

    if not hotspot:
        flash("Hotspot not found.", "danger")
        return redirect(url_for("hotspots.list_hotspots"))
    
    if str(hotspot["created_by"]) != session.get("user_id"):
        flash("You can only delete hotspots you submitted.", "danger")
        return redirect(url_for("hotspots.list_hotspots"))

    try:
        Hotspot.delete_hotspot(hotspot_id, db)
        flash("Hotspot deleted successfully!", "success")
    except Exception as e:
        flash("Error deleting hotspot. Please try again.", "danger")
    
    return redirect(url_for("hotspots.list_hotspots"))

@hotspots_bp.route("/my-hotspots")
@login_required 
def my_hotspots():
    """Show user's own hotspots"""
    db = current_app.db
    user_id = session.get("user_id")
    
    try:
        hotspots = Hotspot.get_hotspots_by_user(user_id, db)
        return render_template("hotspots/my_hotspots.html", hotspots=hotspots)
    except Exception as e:
        flash("Error loading your hotspots.", "danger")
        return redirect(url_for("auth.dashboard"))
