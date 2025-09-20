import json
import os
from datetime import datetime

class ProfileManager:
    def __init__(self, profiles_file="data/profiles.json"):
        self.profiles_file = profiles_file
        self.profiles = self.load_profiles()
    
    def load_profiles(self):
        os.makedirs(os.path.dirname(self.profiles_file), exist_ok=True)
        try:
            with open(self.profiles_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_profiles(self):
        with open(self.profiles_file, 'w') as f:
            json.dump(self.profiles, f, indent=2)
    
    def create_profile(self, user_id, profile_data):
        profile_data['created_at'] = datetime.now().isoformat()
        profile_data['updated_at'] = datetime.now().isoformat()
        self.profiles[user_id] = profile_data
        self.save_profiles()
        return profile_data
    
    def get_profile(self, user_id):
        return self.profiles.get(user_id, {})
    
    def update_profile(self, user_id, updates):
        if user_id in self.profiles:
            self.profiles[user_id].update(updates)
            self.profiles[user_id]['updated_at'] = datetime.now().isoformat()
            self.save_profiles()
            return self.profiles[user_id]
        return None
    
    def delete_profile(self, user_id):
        if user_id in self.profiles:
            del self.profiles[user_id]
            self.save_profiles()
            return True
        return False
    
    def get_profile_prompt(self, user_id):
        profile = self.get_profile(user_id)
        if not profile:
            return ""
        
        prompt_parts = []
        
        # User information
        if 'name' in profile:
            prompt_parts.append(f"The user's name is {profile['name']}.")
        if 'age' in profile:
            prompt_parts.append(f"They are {profile['age']} years old.")
        if 'goals' in profile and profile['goals']:
            goals = ', '.join(profile['goals']) if isinstance(profile['goals'], list) else profile['goals']
            prompt_parts.append(f"Their goals include: {goals}.")
        if 'dietary_preferences' in profile and profile['dietary_preferences']:
            prompt_parts.append(f"Their dietary preferences: {profile['dietary_preferences']}.")
        if 'fitness_level' in profile and profile['fitness_level']:
            prompt_parts.append(f"Their fitness level: {profile['fitness_level']}.")
        if 'interests' in profile and profile['interests']:
            interests = ', '.join(profile['interests']) if isinstance(profile['interests'], list) else profile['interests']
            prompt_parts.append(f"Their interests: {interests}.")
        
        # AI Tone Instructions
        tone_instructions = {
            'professional': "Respond in a formal, business-like manner with complete sentences and proper grammar.",
            'friendly': "Respond in a warm, approachable way, as if talking to a friend.",
            'casual': "Respond in a relaxed, informal way, using casual language and contractions.",
            'humorous': "Respond with a light-hearted, funny tone, including jokes or witty remarks when appropriate.",
            'motivational': "Respond in an encouraging, uplifting way, providing positive reinforcement and motivation.",
            'empathetic': "Respond with understanding and compassion, showing that you care about the user's feelings.",
            'concise': "Keep responses brief and to the point, avoiding unnecessary details.",
            'detailed': "Provide thorough, detailed responses with explanations and examples when helpful."
        }
        
        ai_tone = profile.get('ai_tone', 'professional')
        if ai_tone in tone_instructions:
            prompt_parts.append(tone_instructions[ai_tone])
        
        return " ".join(prompt_parts)