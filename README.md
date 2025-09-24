<div align="center">
  <h1>🤖 AI Personal Assistant</h1>
  <p>A modern, interactive AI chat interface built with Flask and Ollama</p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
  [![Docker](https://img.shields.io/badge/Docker-Support-2496ED?logo=docker)](https://www.docker.com/)
  [![Ollama](https://img.shields.io/badge/Ollama-LLM-FF6C37?logo=openai)](https://ollama.ai/)

  <img src="https://via.placeholder.com/1200x600/2563eb/ffffff?text=AI+Chat+Assistant+Demo" alt="AI Chat Assistant Demo" style="border-radius: 10px; margin: 20px 0; max-width: 100%;">
</div>

## ✨ Features

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0;">
  <div style="background: #f8fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #2563eb;">
    <h3>🤖 AI-Powered Conversations</h3>
    <p>Integrated with Ollama's powerful language models for intelligent, contextual responses.</p>
  </div>
  
  <div style="background: #f8fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #10b981;">
    <h3>💾 Smart Chat Management</h3>
    <p>Save, organize, and manage your conversation history with ease.</p>
  </div>
  
  <div style="background: #f8fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #8b5cf6;">
    <h3>👤 Personalized Experience</h3>
    <p>Create custom profiles to tailor the assistant to your needs.</p>
  </div>
  
  <div style="background: #f8fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #f59e0b;">
    <h3>📱 Responsive Design</h3>
    <p>Beautiful UI that works seamlessly across all devices.</p>
  </div>
</div>

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) (for local AI processing)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account (for data storage)
- Node.js 14+ (for frontend development)
- Docker (optional, for containerized deployment)

## 🖥️ Local Development Setup

### 1. Install Ollama Locally

First, install and set up Ollama on your local machine:

```bash
# Download and install Ollama from https://ollama.ai/download
# Then pull a model (e.g., llama3.1:8b)
ollama pull llama3.1:8b

# Start the Ollama server (keep this running in a separate terminal)
ollama serve
```

### 2. Set Up MongoDB Atlas

1. Create a MongoDB Atlas account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Configure network access to allow connections from your application
4. Create a database user with appropriate permissions
5. Get your connection string from the Atlas dashboard

### 3. Configure MongoDB Connection

Update the [.env](file:///d:/my%20projects/YOUTUBE%20PROJECTS%20AND%20TUTORIALS/PYTHON%20RELATED%20PROJECTS/209025_new_ai_personal_assistant/ai_chat_app/.env) file with your MongoDB Atlas connection string:

```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/ai_chat_app?retryWrites=true&w=majority
```

### 4. Set Up the Application

#### Option A: Python Virtual Environment (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/divyaraj25/AI_CHAT_APP.git
cd ai-personal-assistant/ai_chat_app

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt

# Initialize MongoDB with existing data (if any)
cd backend
python init_mongo.py

# Start the Flask backend
python app.py
```

#### Option B: Docker (Containerized)

```bash
# Navigate to the project directory
cd ai_chat_app

# Update the .env file with your MongoDB Atlas connection string
# Then start the application (it will connect to your MongoDB Atlas instance)
docker-compose up -d --build
```

### 5. Access the Application

Open your browser and navigate to `http://localhost:5000`

## 🔄 Connecting to Local Ollama

The application is configured to connect to Ollama at `http://localhost:11434` by default. If your Ollama instance is running on a different port or host, you can set the `OLLAMA_URL` environment variable:

```bash
# When running with Python
export OLLAMA_URL=http://your-ollama-host:port
python backend/app.py

# Or with Docker
docker-compose run -e OLLAMA_URL=http://host.docker.internal:11434 ai-chat-app
```

## 🔄 MongoDB Configuration

The application uses MongoDB Atlas for data storage. You need to configure the connection string in the [.env](file:///d:/my%20projects/YOUTUBE%20PROJECTS%20AND%20TUTORIALS/PYTHON%20RELATED%20PROJECTS/209025_new_ai_personal_assistant/ai_chat_app/.env) file:

```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/ai_chat_app?retryWrites=true&w=majority
```

To initialize MongoDB with existing JSON data from the `data/` directory, run:

```bash
cd backend
python init_mongo.py
```

This script will:
1. Connect to your MongoDB Atlas instance
2. Create the `ai_chat_app` database
3. Create collections for chat history, profiles, and prompts
4. Migrate existing data from JSON files to MongoDB (if available)
5. Create empty collections if no JSON data exists

## 🐳 Docker Compose Configuration

The Docker setup includes:

- The AI Chat Application (Flask backend + frontend)
- Automatic connection to your local Ollama instance
- Connection to your MongoDB Atlas instance
- Persistent storage for chat history and logs

To rebuild the containers after making changes:

```bash
docker-compose down
docker-compose up -d --build
```

## 🎯 Key Categories

<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; margin: 20px 0;">
  <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; border-left: 3px solid #0ea5e9;">
    <h4>📅 Daily Life</h4>
    <p>Productivity tips, time management, and lifestyle advice</p>
  </div>
  
  <div style="background: #f0fdf4; padding: 15px; border-radius: 8px; border-left: 3px solid #10b981;">
    <h4>💪 Personal Trainer</h4>
    <p>Workout routines, fitness advice, and exercise guidance</p>
  </div>
  
  <div style="background: #f8fafc; padding: 15px; border-radius: 8px; border-left: 3px solid #64748b;">
    <h4>🍽️ Meal Planning</h4>
    <p>Diet plans, nutrition advice, and meal preparation</p>
  </div>
  
  <div style="background: #fef2f2; padding: 15px; border-radius: 8px; border-left: 3px solid #ef4444;">
    <h4>👨‍🍳 Recipe Khazana</h4>
    <p>Cooking recipes, culinary tips, and food ideas</p>
  </div>
  
  <div style="background: #f5f3ff; padding: 15px; border-radius: 8px; border-left: 3px solid #8b5cf6;">
    <h4>📚 GATE Preparation</h4>
    <p>Study resources, exam strategies, and subject guidance</p>
  </div>
  
  <div style="background: #ecfdf5; padding: 15px; border-radius: 8px; border-left: 3px solid #10b981;">
    <h4>❓ General Q&A</h4>
    <p>Get answers to your questions on various topics</p>
  </div>
</div>

## 🛠️ Project Structure

```text
ai-chat-app/
├── backend/          # Flask application and backend logic
│   ├── app.py
│   ├── chat_manager.py
│   ├── profile_manager.py
│   ├── db_manager.py
│   ├── init_mongo.py
│   ├── logger.py
│   ├── prompt_manager.py
│   └── requirements.txt
├── frontend/         # HTML, CSS, and JavaScript files
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── script.js
│   │   └── images/
│   └── templates/
│       └── index.html
├── data/            # JSON files for profiles, chat history, and prompts
│   ├── profiles.json
│   ├── chat_history.json
│   └── prompts.json
├── logs/            # Application logs
│   ├── backend.log
│   ├── frontend.log
│   └── chat.log
├── docker-compose.yml
├── Dockerfile
├── .env
├── .gitignore
├── setup.py
└── README.md
```

---

### Logging

The application maintains detailed logs in the `logs/` directory: