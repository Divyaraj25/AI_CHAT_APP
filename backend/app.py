from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from chat_manager import ChatManager
from profile_manager import ProfileManager
from prompt_manager import PromptManager
from logger import logger
import uuid
import os
import json

# initialize variables
MISSING_USER_ID = "Missing user_id"

app = Flask(__name__, 
            static_folder='../frontend/static',
            template_folder='../frontend/templates')
CORS(app)

# Initialize managers
chat_manager = ChatManager()
profile_manager = ProfileManager()
prompt_manager = PromptManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_id = data.get('user_id')
        chat_id = data.get('chat_id')
        message = data.get('message')
        
        if not user_id or not message:
            return jsonify({"error": "Missing user_id or message"}), 400
        
        # Create a new chat if no chat_id provided
        if not chat_id:
            chat_title = chat_manager.generate_title(message)
            chat_id = chat_manager.create_chat(user_id, chat_title)
        
        # Add user message to chat
        chat_manager.add_message(user_id, chat_id, "user", message)
        
        # Get chat history
        messages = chat_manager.get_chat_messages(user_id, chat_id)
        
        # Get profile context
        profile_context = profile_manager.get_profile_prompt(user_id)
        
        # Log the chat
        logger.log_chat("info", f"User message: {message}", user_id=user_id, chat_id=chat_id)
        
        def generate():
            assistant_response = ""
            for chunk in chat_manager.send_to_ollama(messages, profile_context=profile_context):
                chunk_data = json.loads(chunk)
                
                if chunk_data.get('type') == 'content':
                    content = chunk_data['content']
                    assistant_response += content
                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                
                elif chunk_data.get('type') == 'error':
                    yield f"data: {json.dumps({'type': 'error', 'content': chunk_data['content']})}\n\n"
                    break
                
                elif chunk_data.get('type') == 'done':
                    # Save assistant response to chat history
                    chat_manager.add_message(user_id, chat_id, "assistant", assistant_response)
                    logger.log_chat("info", f"Assistant response: {assistant_response}", user_id=user_id, chat_id=chat_id)
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    break
            
            yield "data: [DONE]\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
    
    except Exception as e:
        logger.log_backend("error", f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/chats', methods=['GET'])
def get_chats():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": MISSING_USER_ID}), 400
    
    chats = chat_manager.get_user_chats(user_id)
    return jsonify(chats)

@app.route('/api/chats/<chat_id>/title', methods=['PUT'])
def update_chat_title(chat_id):
    """Update the title of a chat.
    
    Request body should be JSON with 'user_id' and 'title' fields.
    """
    data = request.json
    user_id = data.get('user_id')
    new_title = data.get('title')
    
    if not user_id:
        return jsonify({"error": MISSING_USER_ID}), 400
    if not new_title or not new_title.strip():
        return jsonify({"error": "Title cannot be empty"}), 400
    
    if chat_manager.update_chat_title(user_id, chat_id, new_title):
        return jsonify({"message": "Chat title updated successfully"})
    return jsonify({"error": "Failed to update chat title"}), 400

@app.route('/api/chats/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": MISSING_USER_ID}), 400
    
    if chat_manager.delete_chat(user_id, chat_id):
        return jsonify({"message": "Chat deleted"})
    return jsonify({"error": "Chat not found"}), 404

@app.route('/api/chats', methods=['DELETE'])
def delete_all_chats():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": MISSING_USER_ID}), 400
    
    if chat_manager.delete_all_chats(user_id):
        return jsonify({"message": "All chats deleted"})
    return jsonify({"error": "User not found"}), 404

@app.route('/api/profile', methods=['GET', 'POST', 'PUT'])
def manage_profile():
    user_id = request.args.get('user_id') or request.json.get('user_id')
    if not user_id:
        return jsonify({"error": MISSING_USER_ID}), 400
    
    if request.method == 'GET':
        profile = profile_manager.get_profile(user_id)
        return jsonify(profile)
    
    elif request.method == 'POST':
        profile_data = request.json
        profile = profile_manager.create_profile(user_id, profile_data)
        return jsonify(profile)
    
    elif request.method == 'PUT':
        updates = request.json
        profile = profile_manager.update_profile(user_id, updates)
        if profile:
            return jsonify(profile)
        return jsonify({"error": "Profile not found"}), 404

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    category = request.args.get('category')
    if category:
        prompts = prompt_manager.get_prompts_by_category(category)
    else:
        prompts = prompt_manager.prompts
    return jsonify(prompts)

@app.route('/api/prompts/categories', methods=['GET'])
def get_categories():
    categories = prompt_manager.get_all_categories()
    return jsonify(categories)

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    logger.log_backend("info", "Starting AI Chat Server")
    app.run(debug=True, host='0.0.0.0', port=5000)