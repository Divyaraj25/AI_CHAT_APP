import json
import uuid
from datetime import datetime
import requests
from db_manager import DatabaseManager

class ChatManager:
    def __init__(self, ollama_url=None):
        self.db_manager = DatabaseManager()
        self.ollama_url = ollama_url or f"http://localhost:11434"
        print(f"Connecting to Ollama at: {self.ollama_url}")  # For debugging
    
    def get_user_chats(self, user_id):
        return self.db_manager.get_user_chats(user_id)
    
    def create_chat(self, user_id, title="New Chat"):
        return self.db_manager.create_chat(user_id, title)
    
    def add_message(self, user_id, chat_id, role, content):
        return self.db_manager.add_message(user_id, chat_id, role, content)
    
    def get_chat_messages(self, user_id, chat_id):
        return self.db_manager.get_chat_messages(user_id, chat_id)
    
    def delete_chat(self, user_id, chat_id):
        return self.db_manager.delete_chat(user_id, chat_id)
    
    def delete_all_chats(self, user_id):
        return self.db_manager.delete_all_chats(user_id)
        
    def update_chat_title(self, user_id, chat_id, new_title):
        """Update the title of a chat.
        
        Args:
            user_id: ID of the user
            chat_id: ID of the chat to update
            new_title: New title for the chat
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        return self.db_manager.update_chat_title(user_id, chat_id, new_title)
    
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