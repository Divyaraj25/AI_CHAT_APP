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

# Configure CORS with appropriate headers for streaming
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize managers
chat_manager = ChatManager()
profile_manager = ProfileManager()
prompt_manager = PromptManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
        
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
            try:
                assistant_response = ""
                for chunk in chat_manager.send_to_ollama(messages, profile_context=profile_context):
                    # Check if the client disconnected using a more reliable method
                    # Remove the request.environ check as it's not available in this context
                    # Instead, we'll rely on the generator being closed when client disconnets
                    
                    try:
                        chunk_data = json.loads(chunk)
                        
                        if chunk_data.get('type') == 'content':
                            content = chunk_data['content']
                            assistant_response += content
                            # Send immediately without buffering
                            yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                        
                        elif chunk_data.get('type') == 'error':
                            error_msg = chunk_data.get('content', 'Unknown error')
                            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
                            logger.log_backend("error", f"Error in chat stream: {error_msg}")
                            break
                        
                        elif chunk_data.get('type') == 'done':
                            # Save assistant response to chat history
                            if assistant_response.strip():  # Only save if we have content
                                chat_manager.add_message(user_id, chat_id, "assistant", assistant_response)
                                logger.log_chat("info", f"Assistant response saved: {len(assistant_response)} chars", user_id=user_id, chat_id=chat_id)
                            yield f"data: {json.dumps({'type': 'done'})}\n\n"
                            break
                            
                    except json.JSONDecodeError as e:
                        logger.log_backend("error", f"JSON decode error in chat stream: {str(e)}")
                        continue
                    except Exception as e:
                        logger.log_backend("error", f"Error processing chunk: {str(e)}")
                        yield f"data: {json.dumps({'type': 'error', 'content': 'An error occurred while processing the response'})}\n\n"
                        break
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                error_msg = f"Error in generate(): {str(e)}"
                logger.log_backend("error", error_msg)
                yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
        
        # Create response with streaming headers
        response = Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',  # Disable buffering in nginx
                'Content-Encoding': 'none'  # Required for some proxies
            }
        )
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        
        return response
    
    except Exception as e:
        logger.log_backend("error", f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/chats', methods=['GET', 'POST'])
def handle_chats():
    if request.method == 'POST':
        # Handle chat creation
        try:
            data = request.json
            user_id = data.get('user_id')
            title = data.get('title', 'New Chat')
            
            if not user_id:
                return jsonify({"error": MISSING_USER_ID}), 400
                
            # Create a new chat
            chat_id = chat_manager.create_chat(user_id, title)
            return jsonify({
                "status": "success",
                "chat_id": chat_id,
                "title": title
            }), 201
            
        except Exception as e:
            logger.log_backend("error", f"Error creating chat: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    else:
        # Handle GET request for chat list
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": MISSING_USER_ID}), 400

        try:
            chats = chat_manager.get_user_chats(user_id)
            return jsonify(chats)
        except Exception as e:
            logger.log_backend("error", f"Error getting chats: {str(e)}")
            return jsonify({"error": str(e)}), 500

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
    
    # Run the application with development settings
    logger.log_backend("info", "Starting AI Chat Server")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True, threaded=True)