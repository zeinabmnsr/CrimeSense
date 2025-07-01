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
    contacts = EmergencyContact.get_contacts_by_user(user_id, db)

    for contact in contacts:
        contact['_id'] = str(contact['_id'])
        contact['user_id'] = str(contact['user_id'])

    return jsonify(contacts), 200


@contacts_api.route('/create', methods=['POST'])
@jwt_required()
def create_contact():
    user_id = get_jwt_identity()
    db = current_app.db
    data = request.get_json()

    name = data.get("name")
    phone = data.get("phone")

    if not name or not phone:
        return jsonify({"error": "Missing contact name or phone"}), 400

    # Wrap validation in a try-except because you're using WTForms-style validator
    try:
        class Dummy:
            data = phone
        validate_phone_number(None, Dummy())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    contact_data = {
        "user_id": user_id,
        "name": name,
        "phone_number": phone
    }

    contact_id = EmergencyContact.create_contact(contact_data, db)
    return jsonify({"message": "Contact created", "id": str(contact_id)}), 201


@contacts_api.route('/<contact_id>', methods=['PUT'])
@jwt_required()
def update_contact(contact_id):
    user_id = get_jwt_identity()
    db = current_app.db
    data = request.get_json()

    name = data.get("name")
    phone = data.get("phone")

    if not name or not phone:
        return jsonify({"error": "Missing contact name or phone"}), 400

    try:
        class Dummy:
            data = phone
        validate_phone_number(None, Dummy())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    contact = EmergencyContact.get_contact_by_id(contact_id, db)
    if not contact or str(contact['user_id']) != str(user_id):
        return jsonify({"error": "Contact not found or unauthorized"}), 404

    update_data = {
        "name": name,
        "phone_number": phone
    }

    EmergencyContact.update_contact(contact_id, update_data, db)
    return jsonify({"message": "Contact updated"}), 200


@contacts_api.route('/<contact_id>', methods=['DELETE'])
@jwt_required()
def delete_contact(contact_id):
    user_id = get_jwt_identity()
    db = current_app.db

    contact = EmergencyContact.get_contact_by_id(contact_id, db)
    if not contact or str(contact['user_id']) != str(user_id):
        return jsonify({"error": "Contact not found or unauthorized"}), 404

    EmergencyContact.delete_contact(contact_id, db)
    return jsonify({"message": "Contact deleted"}), 200
