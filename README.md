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

### 2. Set Up the Application

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

# Start the Flask backend
cd backend
python app.py
```

#### Option B: Docker (Containerized)

```bash
# Navigate to the project directory
cd ai_chat_app

# Start the application (it will connect to your local Ollama instance)
docker-compose up -d --build
```

### 3. Access the Application

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

## 🐳 Docker Compose Configuration

The Docker setup includes:

- The AI Chat Application (Flask backend + frontend)
- Automatic connection to your local Ollama instance
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
│   ├── logger.py
│   ├── prompts.py
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
├── .gitignore
├── setup.py
└── README.md
```

---

### Logging

The application maintains detailed logs in the `logs/` directory:

- **backend.log:** Server-side events and errors
- **frontend.log:** Client-side interactions
- **chat.log:** All chat messages and interactions

---

### API Endpoints

- `GET /` - Serve the main interface
- `POST /api/chat` - Send a message and receive AI response
- `GET /api/chats` - Retrieve chat history
- `DELETE /api/chats/<chat_id>` - Delete a specific chat
- `DELETE /api/chats` - Delete all chats for a user
- `GET|POST|PUT /api/profile` - Manage user profiles
- `GET /api/prompts` - Retrieve prompt suggestions
- `GET /api/prompts/categories` - Get all available categories

---

### Project Valuation

This AI Chat Assistant represents a significant value proposition in the growing market of personalized AI assistants. Based on current market trends and comparable products, the valuation ranges are:

- **Tier 1: Basic Version (Current Implementation)**
  - Estimated Value: $5,000 - $15,000
  - Features: Local deployment, basic chat functionality, profile management
- **Tier 2: Enhanced Version**
  - Estimated Value: $20,000 - $50,000
  - Additional Features: Multi-user support, cloud synchronization, mobile app, premium AI models
- **Tier 3: Enterprise Version**
  - Estimated Value: $75,000 - $150,000+
  - Additional Features: Custom AI training, API access, white-label solutions, advanced analytics

---

### Market Potential

The global chatbot market is expected to reach $10.5 billion by 2026, with personalized AI assistants representing a growing segment. This project addresses multiple verticals (health, education, productivity) making it highly valuable.

---

### Contributing

1.  Fork the repository
2.  Create a feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add amazing feature'`)
4.  Push to the branch (`git push origin feature/amazing-feature`)
5.  Open a Pull Request

---

### License

This project is licensed under the MIT License - see the LICENSE file for details.

---

### Support

For support, please open an issue in the GitHub repository or contact the development team.

---

### Acknowledgments

- Ollama for providing the AI backend
- Flask community for the excellent web framework
- Font Awesome for the icons
- All contributors who help improve this project

---

### How This Project Helps the World

This AI Chat Assistant has the potential to positively impact users worldwide by:

- **Democratizing AI Access:** Provides free, local AI assistance without requiring expensive subscriptions.
- **Personal Development:** Helps users improve their daily lives through personalized advice on fitness, nutrition, and productivity.
- **Educational Support:** Assists students in exam preparation, especially for competitive exams like GATE.
- **Health & Wellness:** Promotes healthy living through meal planning and fitness guidance.
- **Privacy-Focused:** All data remains locally stored, ensuring user privacy and security.
- **Open Source:** Allows developers to contribute and customize the assistant for specific needs.

The application is particularly valuable in regions where access to professional trainers, nutritionists, or tutors may be limited or expensive, making expert guidance more accessible to everyone.

---

## 👨‍💻 Author

- **Name:** Divyaraj Makwana
- **GitHub:** [@divyaraj25](https://github.com/divyaraj25)
- **Email:** divyaraj.makwana9425@gmail.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Divyarajsinh Zala

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
