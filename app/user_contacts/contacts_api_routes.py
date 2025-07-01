# crimesense/user_contacts/contacts_api_routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from app.models.contacts import EmergencyContact
from app.user_contacts.contacts_forms import validate_phone_number

contacts_api = Blueprint('contacts_api', __name__, url_prefix='/api/contacts')

@contacts_api.route('/', methods=['GET'])
@jwt_required()
def get_contacts():
    user_id = get_jwt_identity()
    db = current_app.db
    contacts = EmergencyContact.get_by_user(user_id, db)
    return jsonify(contacts), 200

@contacts_api.route('/create', methods=['POST'])
@jwt_required()
def create_contact():
    user_id = get_jwt_identity()
    db = current_app.db
    data = request.json

    name = data.get("name")
    phone = data.get("phone")

    if not name or not phone:
        return jsonify({"error": "Missing contact name or phone"}), 400

    if not validate_phone_number(phone):
        return jsonify({"error": "Invalid phone number format"}), 400

    contact_id = EmergencyContact.create(name, phone, user_id, db)
    return jsonify({"message": "Contact created", "id": str(contact_id)}), 201

@contacts_api.route('/<contact_id>', methods=['PUT'])
@jwt_required()
def update_contact(contact_id):
    user_id = get_jwt_identity()
    db = current_app.db
    data = request.json

    name = data.get("name")
    phone = data.get("phone")

    if not name or not phone:
        return jsonify({"error": "Missing contact name or phone"}), 400

    if not validate_phone_number(phone):
        return jsonify({"error": "Invalid phone number format"}), 400

    updated = EmergencyContact.update(contact_id, name, phone, user_id, db)
    if not updated:
        return jsonify({"error": "Contact not found or unauthorized"}), 404

    return jsonify({"message": "Contact updated"}), 200

@contacts_api.route('/<contact_id>', methods=['DELETE'])
@jwt_required()
def delete_contact(contact_id):
    user_id = get_jwt_identity()
    db = current_app.db

    deleted = EmergencyContact.delete(contact_id, user_id, db)
    if not deleted:
        return jsonify({"error": "Contact not found or unauthorized"}), 404

    return jsonify({"message": "Contact deleted"}), 200
