#!/usr/bin/env python3
"""
Configuration file for AI Tools module

This file contains configuration settings for the PDF description generation system.
"""

import os
from typing import Optional

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# Alternative models (if you want to use different ones)
AVAILABLE_MODELS = {
    'gpt-4o': 'Most capable, highest cost',
    'gpt-4o-mini': 'Good balance of capability and cost (recommended)',
    'gpt-3.5-turbo': 'Fastest, lowest cost, good for simple tasks'
}

# Text processing configuration
MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', '8000'))  # Characters
MAX_TOKENS_PER_DESCRIPTION = int(os.getenv('MAX_TOKENS_PER_DESCRIPTION', '150'))
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.1'))  # Low for consistency
TIMEOUT_SECONDS = int(os.getenv('TIMEOUT_SECONDS', '30'))

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Rate limiting (optional)
REQUESTS_PER_MINUTE = int(os.getenv('REQUESTS_PER_MINUTE', '60'))
DELAY_BETWEEN_REQUESTS = float(os.getenv('DELAY_BETWEEN_REQUESTS', '1.0'))

def validate_config() -> bool:
    """
    Validate the configuration settings.
    
    Returns:
        True if configuration is valid, False otherwise
    """
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY environment variable is not set")
        print("   Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    if OPENAI_MODEL not in ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo']:
        print(f"⚠️  Warning: OPENAI_MODEL '{OPENAI_MODEL}' is not in the recommended list")
        print(f"   Recommended models: {', '.join(AVAILABLE_MODELS.keys())}")
    
    print("✅ Configuration validation passed")
    return True

def print_config():
    """Print the current configuration settings."""
    print("AI Tools Configuration:")
    print(f"  OpenAI Model: {OPENAI_MODEL}")
    print(f"  Max Text Length: {MAX_TEXT_LENGTH} characters")
    print(f"  Max Tokens: {MAX_TOKENS_PER_DESCRIPTION}")
    print(f"  Temperature: {TEMPERATURE}")
    print(f"  Timeout: {TIMEOUT_SECONDS} seconds")
    print(f"  Rate Limit: {REQUESTS_PER_MINUTE} requests/minute")
    print(f"  Delay: {DELAY_BETWEEN_REQUESTS} seconds between requests")

if __name__ == "__main__":
    print_config()
    validate_config()
