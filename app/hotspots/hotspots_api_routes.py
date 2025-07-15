from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from app.models.hotspot import Hotspot
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from datetime import datetime

hotspots_api_bp = Blueprint("hotsopts_api", __name__, url_prefix="/api/hotspots")
'''
@hotspots_api_bp.route("/hotspots", methods=['GET'])
@jwt_required()
def get_hotspots():
    db = current_app.db 
    current_user_id = get_jwt_identity #i think ma bdna hay
    hotspots = Hotspot.get_all_hotspots(db) #fena nzed filter=loc = current loc aw user loc
    return jsonify(hotspots), 200
'''
# we modified the route from get_all_hotspots to /
@hotspots_api_bp.route("/", methods=['GET'])
@jwt_required() 
def get_hotspots():
    """Get all hotspots with optional filters"""
    db = current_app.db
    
    # Build filters from query parameters
    filters = {}
    if 'crime_type' in request.args:
        filters['crime_type'] = request.args['crime_type']
    if 'location' in request.args:
        # Using regex for partial matching on location 
        filters['location'] = {"$regex": request.args['location'], "$options": "i"}
    if 'danger_time' in request.args:
        try: 
            search_date = datetime.strptime(request.args['danger_time'], "%Y-%m-%d")
            filters['danger_time'] = {
                "$gte": datetime(search_date.year, search_date.month, search_date.day),
                "$lte": datetime(search_date.year, search_date.month, search_date.day, 23, 59, 59)
            }
        except ValueError:
            return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
    
    try:
        hotspots = Hotspot.get_all_hotspots(db, filters=filters)
        for hotspot in hotspots:
            hotspot['_id'] = str(hotspot['_id'])
            hotspot['created_by'] = str(hotspot['created_by'])
            if 'danger_time' in hotspot and hotspot['danger_time']:
                hotspot['danger_time'] = hotspot['danger_time'].isoformat()
            if 'created_at' in hotspot and hotspot['created_at']:
                hotspot['created_at'] = hotspot['created_at'].isoformat()
        
        return jsonify(hotspots), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch hotspots"}), 500 
