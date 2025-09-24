import json
import os
from datetime import datetime
from db_manager import DatabaseManager

class ProfileManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def create_profile(self, user_id, profile_data):
        return self.db_manager.create_profile(user_id, profile_data)
    
    def get_profile(self, user_id):
        return self.db_manager.get_profile(user_id)
    
    def update_profile(self, user_id, updates):
        return self.db_manager.update_profile(user_id, updates)
    
    def delete_profile(self, user_id):
        return self.db_manager.delete_profile(user_id)
    
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