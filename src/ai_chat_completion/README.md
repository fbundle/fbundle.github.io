# AI Chat Completion Tools

This module provides AI-powered tools for generating descriptions of PDF documents using the DeepSeek-R1-Distill-Qwen-1.5B model.

## Features

- **AI Description Generation**: Uses transformer models to generate intelligent descriptions of documents
- **Memory Management**: Automatically handles memory constraints and input truncation
- **Batch Processing**: Processes documents in batches to avoid memory issues
- **Fallback Support**: Falls back to simple descriptions if AI processing fails
- **Configurable**: Easy-to-modify configuration file for different use cases

## Configuration

Edit `ai_config.py` to customize the behavior:

```python
# Disable AI model to always use simple descriptions
USE_AI_MODEL = False

# Adjust memory limits
MAX_CHARS_PER_DOC = 300      # Reduce for lower memory usage
MAX_TOTAL_INPUT = 4000       # Reduce for lower memory usage

# Change batch size
BATCH_SIZE = 2               # Smaller batches use less memory

# Change device
DEVICE = "cpu"               # Use CPU instead of GPU/MPS
```

## Usage

### Basic Usage

```python
from src.ai_chat_completion import ai_tools

# Generate AI descriptions
summary, descriptions = ai_tools.get_ai_description(text_dict)

# Generate simple descriptions (no AI model required)
summary, descriptions = ai_tools.get_ai_description_simple(text_dict)

# Process in batches to avoid memory issues
summary, descriptions = ai_tools.get_ai_description_batched(text_dict, batch_size=2)

# Generate AI description for a single document (for generate_text.py)
# Option 1: Direct function call (loads model each time)
description = ai_tools.get_ai_doc_description(text_content)

# Option 2: Class-based approach (loads model once, more efficient)
model = ai_tools.get_doc_description_model()
description = model.get_ai_doc_description(text_content)
```

### Input Format

#### For Multiple Documents
`text_dict` should be a dictionary mapping PDF file paths to their text content:

```python
text_dict = {
    "docs/public_doc/calculus.pdf": "This document covers fundamental calculus concepts...",
    "docs/public_doc/linear_algebra.pdf": "Linear algebra fundamentals covering vectors...",
}
```

#### For Single Document
`text_content` should be a string containing the extracted text from a single PDF:

```python
text_content = "This document covers fundamental calculus concepts including limits, derivatives, and integrals..."
```

### Output Format

#### For Multiple Documents
Returns a tuple of:
- `summary`: Overall summary of the document collection
- `descriptions`: Dictionary mapping PDF paths to individual descriptions

#### For Single Document
Returns a string:
- `description`: Brief description of the individual document (2-3 sentences)

## Processing Modes

The AI tools support different processing approaches:

1. **Collection Analysis** (`get_ai_description`): Analyze multiple documents together for comprehensive summaries
2. **Individual Analysis** (`get_ai_doc_description`): Process each document separately (used by generate_text.py)
3. **Batch Processing** (`get_ai_description_batched`): Process large collections in memory-efficient batches
4. **Simple Fallback** (`get_ai_description_simple`): Rule-based descriptions without AI processing

## Efficiency Optimization

For processing multiple documents individually (like in `generate_text.py`), use the class-based approach:

```python
# Load model once
model = ai_tools.get_doc_description_model()

# Process multiple documents with the same model instance
for document in documents:
    description = model.get_ai_doc_description(document_text)
```

This approach:
- **Loads the AI model only once** instead of for each document
- **Significantly reduces processing time** for multiple documents
- **Maintains memory efficiency** by reusing the loaded model
- **Provides better error handling** with fallback to simple descriptions

## Troubleshooting

### Memory Issues

If you encounter memory errors:

1. **Reduce input size**: Set `MAX_CHARS_PER_DOC` to a smaller value (e.g., 200-300)
2. **Use batching**: Use `get_ai_description_batched()` with smaller batch sizes
3. **Disable AI**: Set `USE_AI_MODEL = False` to always use simple descriptions
4. **Use CPU**: Set `DEVICE = "cpu"` if GPU/MPS memory is limited

### Model Loading Issues

If the AI model fails to load:

1. Check that your cache directory exists and contains the model files
2. Verify you have enough disk space for the model
3. Ensure you have the required dependencies installed (`torch`, `transformers`)

### Performance Tips

- **Individual documents**: Use `get_ai_doc_description()` for processing one document at a time
- **Small collections**: Use `get_ai_description()` for collections with few, short documents
- **Large collections**: Use `get_ai_description_batched()` for many documents
- **Testing**: Use `get_ai_description_simple()` for quick testing without AI model loading

## Dependencies

- `torch` - PyTorch for model inference
- `transformers` - Hugging Face transformers library
- `pydantic` - Data validation

## Model Information

The default model is `deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B`, a 1.5B parameter model optimized for:
- Document understanding and summarization
- Academic and technical content
- Memory-efficient inference

Model size: ~3GB when loaded into memory.
