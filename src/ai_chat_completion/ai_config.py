#!/usr/bin/env python3
"""
Configuration file for AI tools.
Modify these settings to control AI model behavior and memory usage.
"""

# AI Model Configuration
USE_AI_MODEL = True  # Set to False to always use simple descriptions

# Memory Management
MAX_CHARS_PER_DOC = 1000     # Maximum characters per document (increased for single docs)
MAX_TOTAL_INPUT = 8000       # Maximum total input length before truncation
FALLBACK_THRESHOLD = 12000   # Length threshold to force fallback to simple descriptions

# Batching
BATCH_SIZE = 3               # Number of documents to process in batches

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
DEFAULT_MODEL = "deepseekr1_distill_qwen1p5b_transformers"

# Generation Parameters
GENERATION_KWARGS = {
    "max_new_tokens": 512,   # Reduced for single document descriptions
    "temperature": 0.7,       # Slightly higher for more creative descriptions
    "top_p": 0.9,            # Slightly lower for more focused output
}
