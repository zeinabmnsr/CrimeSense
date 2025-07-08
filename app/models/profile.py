from bson import ObjectId
from datetime import datetime

class Profile:
    def _init_(self, profile_dict):
        self._id = profile_dict["_id"]
        self.id = str(self._id)
        self.user_id = profile_dict["user_id"]
        self.display_name = profile_dict.get("display_name", "")
        self.bio = profile_dict.get("bio", "")
        self.avatar = profile_dict.get("avatar", "")
        self.phone = profile_dict.get("phone", "")
        self.address = profile_dict.get("address", "")
        self.website = profile_dict.get("website", "")
        self.social_media = profile_dict.get("social_media", "")
        self.location = profile_dict.get("location", "")
        self.privacy_settings = profile_dict.get("privacy_settings", {})
        self.notification_preferences = profile_dict.get("notification_preferences", {})
        self.settings = profile_dict.get("settings", {})
        self.created_at = profile_dict.get("created_at", datetime.utcnow())
        self.updated_at = profile_dict.get("updated_at", datetime.utcnow())
        self.deleted = profile_dict.get("deleted", False)

    @classmethod
    def create(cls, user_id, db, **profile_data):
        """Create a new profile for a user."""
        profile = {
            'user_id': ObjectId(user_id),
            'display_name': profile_data.get('display_name', ''),
            'bio': profile_data.get('bio', ''),
            'avatar': profile_data.get('avatar', ''),
            'phone': profile_data.get('phone', ''),
            'address': profile_data.get('address', ''),
            'website': profile_data.get('website', ''),
            'social_media': profile_data.get('social_media', ''),
            'location': profile_data.get('location', ''),
            'privacy_settings': profile_data.get('privacy_settings', {
                'profile_visibility': 'public',
                'show_email': False,
                'show_phone': False,
                'show_location': True
            }),
            'notification_preferences': profile_data.get('notification_preferences', {
                'email_reports': 'immediate',
                'email_alerts': 'immediate',
                'sms_alerts': 'emergency',
                'push_notifications': 'all'
            }),
            'settings': profile_data.get('settings', {
                'language': 'en',
                'timezone': 'UTC',
                'theme': 'light'
            }),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'deleted': False
        }
        
        inserted_profile = db.profiles.insert_one(profile)
        return inserted_profile.inserted_id

    @classmethod
    def get_by_id(cls, profile_id, db):
        """Get profile by ID and return Profile instance."""
        profile_data = db.profiles.find_one({'_id': ObjectId(profile_id), 'deleted': {'$ne': True}})
        if profile_data:
            return cls(profile_data)
        return None

    @classmethod
    def get_by_user_id(cls, user_id, db):
        """Get profile by user ID and return Profile instance."""
        profile_data = db.profiles.find_one({'user_id': ObjectId(user_id), 'deleted': {'$ne': True}})
        if profile_data:
            return cls(profile_data)
        return None

    @classmethod
    def find_by_id(cls, profile_id, db):
        """Find profile by ID and return raw profile data."""
        return db.profiles.find_one({'_id': ObjectId(profile_id), 'deleted': {'$ne': True}})

    @classmethod
    def find_by_user_id(cls, user_id, db):
        """Find profile by user ID and return raw profile data."""
        return db.profiles.find_one({'user_id': ObjectId(user_id), 'deleted': {'$ne': True}})

    @classmethod
    def update_by_user_id(cls, user_id, update_data, db):
        """Update profile by user ID."""
        update_data['updated_at'] = datetime.utcnow()
        result = db.profiles.update_one(
            {'user_id': ObjectId(user_id), 'deleted': {'$ne': True}},
            {'$set': update_data}
        )
        return result.modified_count > 0

    @classmethod
    def update_by_id(cls, profile_id, update_data, db):
        """Update profile by profile ID."""
        update_data['updated_at'] = datetime.utcnow()
        result = db.profiles.update_one(
            {'_id': ObjectId(profile_id), 'deleted': {'$ne': True}},
            {'$set': update_data}
        )
        return result.modified_count > 0

    @classmethod
    def delete_by_user_id(cls, user_id, db, soft_delete=True):
        """Delete profile by user ID (soft delete by default)."""
        if soft_delete:
            result = db.profiles.update_one(
                {'user_id': ObjectId(user_id)},
                {'$set': {'deleted': True, 'deleted_at': datetime.utcnow()}}
            )
            return result.modified_count > 0
        else:
            result = db.profiles.delete_one({'user_id': ObjectId(user_id)})
            return result.deleted_count > 0

    @classmethod
    def delete_by_id(cls, profile_id, db, soft_delete=True):
        """Delete profile by profile ID (soft delete by default)."""
        if soft_delete:
            result = db.profiles.update_one(
                {'_id': ObjectId(profile_id)},
                {'$set': {'deleted': True, 'deleted_at': datetime.utcnow()}}
            )
            return result.modified_count > 0
        else:
            result = db.profiles.delete_one({'_id': ObjectId(profile_id)})
            return result.deleted_count > 0

    @classmethod
    def get_all_profiles(cls, db, limit=50, skip=0):
        """Get all profiles with pagination."""
        profiles = db.profiles.find(
            {'deleted': {'$ne': True}},
            limit=limit,
            skip=skip,
            sort=[('created_at', -1)]
        )
        return [cls(profile) for profile in profiles]

    @classmethod
    def search_profiles(cls, query, db, limit=20):
        """Search profiles by display name or bio."""
        search_filter = {
            'deleted': {'$ne': True},
            '$or': [
                {'display_name': {'$regex': query, '$options': 'i'}},
                {'bio': {'$regex': query, '$options': 'i'}}
            ]
        }
        profiles = db.profiles.find(search_filter, limit=limit)
        return [cls(profile) for profile in profiles]

    @classmethod
    def update_avatar(cls, user_id, avatar_url, db):
        """Update user's avatar."""
        return cls.update_by_user_id(user_id, {'avatar': avatar_url}, db)

    @classmethod
    def update_privacy_settings(cls, user_id, privacy_settings, db):
        """Update user's privacy settings."""
        return cls.update_by_user_id(user_id, {'privacy_settings': privacy_settings}, db)

    @classmethod
    def update_notification_preferences(cls, user_id, notification_preferences, db):
        """Update user's notification preferences."""
        return cls.update_by_user_id(user_id, {'notification_preferences': notification_preferences}, db)

    @classmethod
    def update_settings(cls, user_id, settings, db):
        """Update user's general settings."""
        return cls.update_by_user_id(user_id, {'settings': settings}, db)

    def to_dict(self):
        """Convert Profile instance to dictionary."""
        return {
            '_id': str(self._id),
            'id': self.id,
            'user_id': str(self.user_id),
            'display_name': self.display_name,
            'bio': self.bio,
            'avatar': self.avatar,
            'phone': self.phone,
            'address': self.address,
            'website': self.website,
            'social_media': self.social_media,
            'location': self.location,
            'privacy_settings': self.privacy_settings,
            'notification_preferences': self.notification_preferences,
            'settings': self.settings,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def get_public_data(self):
        """Get public profile data based on privacy settings."""
        public_data = {
            '_id': str(self._id),
            'user_id': str(self.user_id),
            'display_name': self.display_name,
            'bio': self.bio,
            'avatar': self.avatar
        }
        
        # Add fields based on privacy settings
        if self.privacy_settings.get('show_phone', False):
            public_data['phone'] = self.phone
        
        if self.privacy_settings.get('show_location', True):
            public_data['location'] = self.location
            
        if self.privacy_settings.get('show_website', True):
            public_data['website'] = self.website
            
        return public_data

    def is_public(self):
        """Check if profile is public."""
        return self.privacy_settings.get('profile_visibility', 'public') == 'public'

    def can_view(self, viewer_user_id=None):
        """Check if a user can view this profile."""
        visibility = self.privacy_settings.get('profile_visibility', 'public')
        
        if visibility == 'public':
            return True
        elif visibility == 'private':
            return str(self.user_id) == str(viewer_user_id)
        elif visibility == 'friends':
            # This would require a friends/connections system
            # For now, treat as private
            return str(self.user_id) == str(viewer_user_id)
        
        return False