import json
import os
from db_manager import DatabaseManager

class PromptManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.prompts = self.load_prompts()
    
    def load_prompts(self):
        return self.db_manager.get_prompts()
    
    def get_prompts_by_category(self, category):
        return self.db_manager.get_prompts_by_category(category)
    
    def get_all_categories(self):
        return self.db_manager.get_all_categories()
