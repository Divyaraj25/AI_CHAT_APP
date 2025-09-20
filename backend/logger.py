import logging
import os
from datetime import datetime
import json

class CustomLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Define log formats
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # Backend logger
        self.backend_logger = logging.getLogger('backend')
        self.backend_logger.setLevel(logging.INFO)
        backend_handler = logging.FileHandler(f'{log_dir}/backend.log')
        backend_handler.setFormatter(logging.Formatter(log_format, date_format))
        self.backend_logger.addHandler(backend_handler)
        
        # Frontend logger
        self.frontend_logger = logging.getLogger('frontend')
        self.frontend_logger.setLevel(logging.INFO)
        frontend_handler = logging.FileHandler(f'{log_dir}/frontend.log')
        frontend_handler.setFormatter(logging.Formatter(log_format, date_format))
        self.frontend_logger.addHandler(frontend_handler)
        
        # Chat logger
        self.chat_logger = logging.getLogger('chat')
        self.chat_logger.setLevel(logging.INFO)
        chat_handler = logging.FileHandler(f'{log_dir}/chat.log')
        chat_handler.setFormatter(logging.Formatter(log_format, date_format))
        self.chat_logger.addHandler(chat_handler)
        
        # Console handler for all loggers
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format, date_format))
        self.backend_logger.addHandler(console_handler)
        self.frontend_logger.addHandler(console_handler)
        self.chat_logger.addHandler(console_handler)
    
    def log_backend(self, level, message, extra=None):
        log_method = getattr(self.backend_logger, level)
        if extra:
            log_method(message, extra=extra)
        else:
            log_method(message)
    
    def log_frontend(self, level, message, extra=None):
        log_method = getattr(self.frontend_logger, level)
        if extra:
            log_method(message, extra=extra)
        else:
            log_method(message)
    
    def log_chat(self, level, message, user_id=None, chat_id=None):
        extra = {}
        if user_id:
            extra['user_id'] = user_id
        if chat_id:
            extra['chat_id'] = chat_id
            
        log_method = getattr(self.chat_logger, level)
        if extra:
            log_method(message, extra=extra)
        else:
            log_method(message)

# Create global logger instance
logger = CustomLogger()