import json
import os

class PromptManager:
    def __init__(self, prompts_file="data/prompts.json"):
        self.prompts_file = prompts_file
        self.prompts = self.load_prompts()
    
    def load_prompts(self):
        os.makedirs(os.path.dirname(self.prompts_file), exist_ok=True)
        try:
            with open(self.prompts_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Default prompts
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
            self.save_prompts(default_prompts)
            return default_prompts
    
    def save_prompts(self, prompts):
        with open(self.prompts_file, 'w') as f:
            json.dump(prompts, f, indent=2)
    
    def get_prompts_by_category(self, category):
        return self.prompts.get(category, [])
    
    def add_prompt(self, category, prompt):
        if category not in self.prompts:
            self.prompts[category] = []
        self.prompts[category].append(prompt)
        self.save_prompts(self.prompts)
    
    def get_all_categories(self):
        return list(self.prompts.keys())