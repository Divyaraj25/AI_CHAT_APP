import json
import os
import uuid
from datetime import datetime
import requests

class ChatManager:
    def __init__(self, history_file="../data/chat_history.json", ollama_url=None):
        self.history_file = history_file
        self.ollama_url = ollama_url or f"http://{os.getenv('OLLAMA_HOST', 'localhost:11434')}"
        self.chat_history = self.load_history()
        print(f"Connecting to Ollama at: {self.ollama_url}")  # For debugging
    
    def load_history(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.chat_history, f, indent=2)
    
    def get_user_chats(self, user_id):
        return self.chat_history.get(user_id, {})
    
    def create_chat(self, user_id, title="New Chat"):
        chat_id = str(uuid.uuid4())
        if user_id not in self.chat_history:
            self.chat_history[user_id] = {}
        
        self.chat_history[user_id][chat_id] = {
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        self.save_history()
        return chat_id
    
    def add_message(self, user_id, chat_id, role, content):
        if user_id in self.chat_history and chat_id in self.chat_history[user_id]:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            self.chat_history[user_id][chat_id]["messages"].append(message)
            self.chat_history[user_id][chat_id]["updated_at"] = datetime.now().isoformat()
            self.save_history()
            return message
        return None
    
    def get_chat_messages(self, user_id, chat_id):
        if user_id in self.chat_history and chat_id in self.chat_history[user_id]:
            return self.chat_history[user_id][chat_id]["messages"]
        return []
    
    def delete_chat(self, user_id, chat_id):
        if user_id in self.chat_history and chat_id in self.chat_history[user_id]:
            del self.chat_history[user_id][chat_id]
            self.save_history()
            return True
        return False
    
    def delete_all_chats(self, user_id):
        if user_id in self.chat_history:
            self.chat_history[user_id] = {}
            self.save_history()
            return True
        return False
        
    def update_chat_title(self, user_id, chat_id, new_title):
        """Update the title of a chat.
        
        Args:
            user_id: ID of the user
            chat_id: ID of the chat to update
            new_title: New title for the chat
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if (user_id in self.chat_history and 
            chat_id in self.chat_history[user_id] and 
            new_title and 
            new_title.strip()):
            
            self.chat_history[user_id][chat_id]["title"] = new_title.strip()
            self.chat_history[user_id][chat_id]["updated_at"] = datetime.now().isoformat()
            self.save_history()
            return True
            
        return False
    
    def generate_title(self, user_message):
        if len(user_message) > 30:
            return user_message[:27] + "..."
        return user_message
    
    def send_to_ollama(self, messages, model="llama3.1:8b", profile_context=""):
        # Add profile context to the system message if provided
        system_message = {
            "role": "system",
            "content": "You are a helpful AI assistant. " + profile_context
        }
        
        # Prepare the payload for Ollama
        payload = {
            "model": model,
            "messages": [system_message] + messages,
            "stream": True
        }
        
        try:
            # Make request to Ollama with streaming
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                stream=True,
                timeout=300,
                headers={"Content-Type": "application/json"},
                verify=False
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            line = line[6:].strip()
                        
                        if line == '[DONE]':
                            yield json.dumps({"type": "done"})
                            break
                            
                        data = json.loads(line)
                        
                        if data.get('done', False):
                            yield json.dumps({"type": "done"})
                            break
                            
                        if data.get('message') and data['message'].get('content'):
                            chunk = data['message']['content']
                            yield json.dumps({
                                "type": "content",
                                "content": chunk
                            })
                            
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error processing response: {e}")
                        continue
            
        except requests.exceptions.Timeout:
            error_msg = "Error: Request to Ollama timed out."
            yield json.dumps({"type": "error", "content": error_msg})
        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Ollama: {str(e)}"
            yield json.dumps({"type": "error", "content": error_msg})
        except Exception as e:
            error_msg = f"An unexpected error occurred: {str(e)}"
            yield json.dumps({"type": "error", "content": error_msg})