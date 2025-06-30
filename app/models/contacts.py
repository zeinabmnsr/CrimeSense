from bson import ObjectId
from datetime import datetime

class EmergencyContact:
    @staticmethod
    def create_contact(data, db):
        """Create a new emergency contact for a user."""
        contact = {
            "user_id": ObjectId(data["user_id"]),
            "name": data["name"],
            "phone_number": data["phone_number"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        return db.emergency_contacts.insert_one(contact).inserted_id

    @staticmethod
    def get_contacts_by_user(user_id, db):
        """Retrieve all emergency contacts for a specific user."""
        return list(db.emergency_contacts.find({"user_id": ObjectId(user_id)}))

    @staticmethod
    def get_contact_by_id(contact_id, db):
        """Retrieve a single contact by its ID."""
        return db.emergency_contacts.find_one({"_id": ObjectId(contact_id)})

    @staticmethod
    def update_contact(contact_id, update_data, db):
        """Update a contact with new data."""
        update_data["updated_at"] = datetime.utcnow()
        return db.emergency_contacts.update_one(
            {"_id": ObjectId(contact_id)},
            {"$set": update_data}
        )

    @staticmethod
    def delete_contact(contact_id, db):
        """Delete a contact by its ID."""
        return db.emergency_contacts.delete_one({"_id": ObjectId(contact_id)})
