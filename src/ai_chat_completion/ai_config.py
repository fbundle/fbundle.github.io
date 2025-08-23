#!/usr/bin/env python3
"""
Configuration file for AI tools.
Modify these settings to control AI model behavior and memory usage.
"""

# AI Model Configuration
USE_AI_MODEL = True  # Set to False to always use simple descriptions

# Memory Management
MAX_CHARS_PER_DOC = 1000     # Maximum characters per document (increased for single docs)

# Device Selection
# Options: "mps" (Apple Silicon), "cuda" (NVIDIA GPU), "cpu"
DEVICE = "mps"               # Will auto-fallback to CPU if MPS/CUDA not available

# Cache Directory Search Paths
CACHE_DIRS = [
    "/Users/khanh/vault/downloads/model",
    "/home/khanh/Downloads/model/",
    # Add your model cache directories here
]

# Model Selection
DEFAULT_MODEL = "gpt_oss_20b_transformers"


