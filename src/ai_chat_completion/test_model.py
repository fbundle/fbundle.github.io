#!/usr/bin/env python3

import os
from llama_cpp import Llama

def test_model_loading():
    cache_dir = "/Users/khanh/vault/downloads/model"
    
    # Test with the 8B model - smallest and most compatible
    model_path = os.path.join(cache_dir, "lmstudio-community/DeepSeek-R1-0528-Qwen3-8B-GGUF/DeepSeek-R1-0528-Qwen3-8B-Q4_K_M.gguf")
    
    print(f"Testing model: {model_path}")
    print(f"File exists: {os.path.exists(model_path)}")
    print(f"File size: {os.path.getsize(model_path) / (1024**3):.2f} GB")
    
    try:
        print("Attempting to load model...")
        llm = Llama(
            model_path=model_path,
            verbose=True,
            n_gpu_layers=0,  # CPU only for testing
            n_ctx=2048,  # Smaller context for testing
        )
        print("Model loaded successfully!")
        
        # Test a simple completion
        print("Testing completion...")
        response = llm.create_completion(
            "Hello, how are you?",
            max_tokens=10,
            temperature=0.7,
        )
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error loading model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_loading()
