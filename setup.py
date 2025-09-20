#!/usr/bin/env python3

import os
import json
from pathlib import Path
from termcolor import colored

def setup_directories():
    """Create necessary directories"""
    directories = [
        'backend/data',
        'backend/logs',
        'frontend/static/css',
        'frontend/static/js',
        'frontend/static/images',
        'frontend/templates'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(colored(f"Created directory: {directory}", attrs=['bold']))

def create_default_files():
    """Create default data files if they don't exist"""
    # Default profiles file
    profiles_file = Path('backend/data/profiles.json')
    if not profiles_file.exists():
        with open(profiles_file, 'w') as f:
            json.dump({}, f)
        print(colored("Created default profiles.json", attrs=['bold']))
    
    # Default chat history file
    chat_history_file = Path('backend/data/chat_history.json')
    if not chat_history_file.exists():
        with open(chat_history_file, 'w') as f:
            json.dump({}, f)
        print(colored("Created default chat_history.json", attrs=['bold']))
    
    # Default prompts file
    prompts_file = Path('backend/data/prompts.json')
    if not prompts_file.exists():
        default_prompts = {
            "daily_life": [
                "What are some productive habits I can develop?",
                "How can I manage my time better?",
                "What's a good morning routine?"
            ],
            "personal_trainee": [
                "Create a 30-minute workout routine for beginners",
                "How can I improve my posture?",
                "What exercises can I do at home without equipment?"
            ],
            "meal_planner": [
                "Suggest a healthy meal plan for weight loss",
                "What are some high-protein breakfast ideas?",
                "Plan meals for a vegetarian for one week"
            ],
            "recipe_khazana": [
                "Share a quick and easy dinner recipe",
                "How do I make homemade pasta?",
                "What's a good dessert recipe for beginners?"
            ],
            "gate_preparation": [
                "How should I prepare for GATE Computer Science?",
                "What's the best study schedule for GATE?",
                "Recommend resources for GATE preparation"
            ],
            "qna": [
                "Explain quantum computing in simple terms",
                "What's the difference between AI and machine learning?",
                "How does blockchain technology work?"
            ]
        }
        with open(prompts_file, 'w') as f:
            json.dump(default_prompts, f, indent=2)
        print(colored("Created default prompts.json", attrs=['bold']))

if __name__ == '__main__':
    print(colored("Setting up AI Chat Application...", attrs=['bold']))
    setup_directories()
    create_default_files()
    print(colored("Setup completed successfully!", attrs=['bold']))