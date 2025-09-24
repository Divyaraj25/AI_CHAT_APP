import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_mongo_client():
    """Create and return a MongoDB client."""
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_uri)
    return client

def init_mongodb():
    """Initialize MongoDB with data from JSON files."""
    # Connect to MongoDB
    client = get_mongo_client()
    db = client['ai_chat_app']
    
    # Initialize collections
    collections = {
        'chat_history': '../data/chat_history.json',
        'profiles': '../data/profiles.json',
        'prompts': '../data/prompts.json'
    }
    
    for collection_name, file_path in collections.items():
        collection = db[collection_name]
        
        # Check if collection already has data
        if collection.count_documents({}) > 0:
            print(f"Collection '{collection_name}' already has data. Skipping...")
            continue
            
        # Load data from JSON file if it exists
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # For chat_history and profiles, each key is a document
                if collection_name in ['chat_history', 'profiles']:
                    documents = []
                    for key, value in data.items():
                        doc = {'_id': key, **value}
                        documents.append(doc)
                    
                    if documents:
                        collection.insert_many(documents)
                        print(f"Inserted {len(documents)} documents into '{collection_name}' collection")
                    else:
                        # Create empty collection with schema
                        collection.insert_one({'_id': 'placeholder', 'data': {}})
                        collection.delete_one({'_id': 'placeholder'})
                        print(f"Created empty '{collection_name}' collection")
                else:
                    # For prompts, insert as a single document
                    collection.insert_one({'_id': 'prompts', 'data': data})
                    print(f"Inserted prompts data into '{collection_name}' collection")
                    
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading {file_path}: {e}")
                # Create empty collection
                collection.insert_one({'_id': 'placeholder', 'data': {}})
                collection.delete_one({'_id': 'placeholder'})
                print(f"Created empty '{collection_name}' collection")
        else:
            # Create empty collection
            collection.insert_one({'_id': 'placeholder', 'data': {}})
            collection.delete_one({'_id': 'placeholder'})
            print(f"Created empty '{collection_name}' collection")
    
    print("MongoDB initialization completed!")
    client.close()

if __name__ == "__main__":
    init_mongodb()