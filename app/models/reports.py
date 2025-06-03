from datetime import datetime 
from bson import ObjectId 

class CrimeReport:
    def __init__(self, title, description, location, date_occured, crime_type, reported_by,
                 is_public=False, status="Pending", date_repoted=None):
        self.title = title 
        self.description = description 
        self.location = location 
        self.crime_type = crime_type 
        self.date_reported = datetime.utcnow() # when it was reported
        self.date_occured = date_occured # aymta saret el crime
        self.is_public = is_public 
        self.status = status 

    @staticmethod 
    def created_report(data, db):
        """create a new crime report and store it in m db"""
        report = {
            "title": data["title"],
            "description": data["description"],
            "loctation": data["location"],
            "crime_type": data["crime_type"],
            "date_reported": datetime.utcnow(),
            "date_occured": data["date_occured"],
            "reported_by": ObjectId(data["reported_by"]),
            "is_public" : data.get("is_public", False),
            "status": data.get("status", "Pending"),
            "image_path": data.get("image_path")
        }
        #optional nraje3 el inserted_id , fro success msgs or redirects
        return db.crime_reports.insert_one(report) .inserted_id
    @staticmethod 
    def get_report_by_id(report_id, db):
          """Fetch a crime report by ID"""
          return db.crime_reports.find_one({"_id": ObjectId(report_id)})

    @staticmethod 
    def update_report(report_id, update_data, db):
          """Update an existing crime report"""
          return db.crime_reports.update_one(
              {"_id": ObjectId(report_id)},
              {"$set": update_data}
         )
    
    @staticmethod
    def delete_report(report_id, db):
        """Delete a crime report by its ObjectId"""
        db.crime_reports.delete_one({"_id": ObjectId(report_id)})
    
    @staticmethod 
    def get_all_reports(db, filters=None):
        """Retrieve all crime reports, optionally filtered"""
        query = filters if filters else {}
        return list(db.crime_reports.find(query))