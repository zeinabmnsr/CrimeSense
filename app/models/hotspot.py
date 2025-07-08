from datetime import datetime 
from bson import ObjectId 

class Hotspot:
    def __init__(self, crime_type, location, lat, lng, created_by, created_at, danger_time, notes):
        self.crime_type = crime_type 
        self.location = location  
        self.lat = lat 
        self.lng = lng 
        self.created_by = created_by
        self.created_at = created_at #aymta hl alert naaml
        self.danger_time = danger_time #ay waet howe danger lhlcrime 
        self.notes = notes #el notes hye yle rh nb3ata maa el alert aal frontend 

    @staticmethod 
    def create_hotspot(data, db):
        hotspot = {
            "crime_type": data["crime_type"],
            "location": data["location"],
            "lat": data["lat"],
            "lng": data["lng"],
            "created_by": ObjectId(data["created_by"]),
            "created_at": data.get("created_at", datetime.utcnow()),
            "danger_time": data["danger_time"],
            "notes": data["notes"]
        }
        return db.hotspots.insert_one(hotspot).inserted_id

    @staticmethod 
    def get_hotspot_by_id(hotspot_id, db):
        return db.hotspots.find_one({"_id": ObjectId(hotspot_id)})
    
    @staticmethod 
    def update_hotspot(hotspot_id, update_data, db):
        return db.hotspots.update_one(
            {"_id": ObjectId(hotspot_id)},
            {"$set": update_data}
        )
    
    @staticmethod 
    def delete_hotspot(hotspot_id, db):
        db.hotspots.delete_one({"_id": ObjectId(hotspot_id)})

    def get_all_hotspots(db, filters=None): 
        query = filters if filters else {}
        return list(db.hotspots.find(query))