import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        """Initialize the database manager with MongoDB connection."""
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(mongo_uri)
        self.db = self.client['ai_chat_app']
        self.chat_collection = self.db['chat_history']
        self.profile_collection = self.db['profiles']
        self.prompt_collection = self.db['prompts']
    
    def close_connection(self):
        """Close the MongoDB connection."""
        self.client.close()
    
    # Chat History Methods
    def get_user_chats(self, user_id):
        """Get all chats for a user."""
        user_doc = self.chat_collection.find_one({'_id': user_id})
        if user_doc:
            # Remove the _id field and return the rest
            user_doc.pop('_id', None)
            return user_doc
        return {}
    
    def create_chat(self, user_id, title="New Chat"):
        """Create a new chat for a user."""
        chat_id = str(uuid.uuid4())
        chat_data = {
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        
        # Update the user document or create if it doesn't exist
        self.chat_collection.update_one(
            {'_id': user_id},
            {
                '$set': {f'{chat_id}': chat_data},
                '$setOnInsert': {'_id': user_id}
            },
            upsert=True
        )
        
        return chat_id
    
    def add_message(self, user_id, chat_id, role, content):
        """Add a message to a chat."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        result = self.chat_collection.update_one(
            {'_id': user_id},
            {
                '$push': {f'{chat_id}.messages': message},
                '$set': {f'{chat_id}.updated_at': datetime.now().isoformat()}
            }
        )
        
        return message if result.modified_count > 0 else None
    
    def get_chat_messages(self, user_id, chat_id):
        """Get messages for a specific chat."""
        user_doc = self.chat_collection.find_one({'_id': user_id})
        if user_doc and chat_id in user_doc:
            return user_doc[chat_id].get('messages', [])
        return []
    
    def delete_chat(self, user_id, chat_id):
        """Delete a specific chat."""
        result = self.chat_collection.update_one(
            {'_id': user_id},
            {'$unset': {chat_id: ""}}
        )
        return result.modified_count > 0
    
    def delete_all_chats(self, user_id):
        """Delete all chats for a user."""
        result = self.chat_collection.update_one(
            {'_id': user_id},
            {'$set': {}}
        )
        return result.modified_count > 0
    
    def update_chat_title(self, user_id, chat_id, new_title):
        """Update the title of a chat."""
        if not new_title or not new_title.strip():
            return False
            
        result = self.chat_collection.update_one(
            {'_id': user_id},
            {
                '$set': {
                    f'{chat_id}.title': new_title.strip(),
                    f'{chat_id}.updated_at': datetime.now().isoformat()
                }
            }
        )
        
        return result.modified_count > 0
    
    # Profile Methods
    def get_profile(self, user_id):
        """Get user profile."""
        profile = self.profile_collection.find_one({'_id': user_id})
        if profile:
            # Remove the _id field and return the rest
            profile.pop('_id', None)
            return profile
        return {}
    
    def create_profile(self, user_id, profile_data):
        """Create a new user profile."""
        profile_data['created_at'] = datetime.now().isoformat()
        profile_data['updated_at'] = datetime.now().isoformat()
        
        self.profile_collection.update_one(
            {'_id': user_id},
            {'$set': profile_data},
            upsert=True
        )
        
        return profile_data
    
    def update_profile(self, user_id, updates):
        """Update user profile."""
        updates['updated_at'] = datetime.now().isoformat()
        
        result = self.profile_collection.update_one(
            {'_id': user_id},
            {'$set': updates}
        )
        
        if result.modified_count > 0:
            return self.get_profile(user_id)
        return None
    
    def delete_profile(self, user_id):
        """Delete user profile."""
        result = self.profile_collection.delete_one({'_id': user_id})
        return result.deleted_count > 0
    
    # Prompt Methods
    def get_prompts(self):
        """Get all prompts."""
        prompt_doc = self.prompt_collection.find_one({'_id': 'prompts'})
        if prompt_doc and 'data' in prompt_doc:
            return prompt_doc['data']
        return {}
    
    def get_prompts_by_category(self, category):
        """Get prompts by category."""
        prompts = self.get_prompts()
        return prompts.get(category, [])
    
    def get_all_categories(self):
        """Get all prompt categories."""
        prompts = self.get_prompts()
        return list(prompts.keys())