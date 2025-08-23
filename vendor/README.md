# AI Tools for PDF Description Generation

This module provides AI-powered functionality to generate accurate, concise descriptions of PDF documents using OpenAI's GPT models.

## Features

- **Accurate PDF Descriptions**: Generate precise descriptions based on extracted text content
- **Academic Document Support**: Optimized for mathematical and academic documents
- **Configurable**: Easy to customize models, parameters, and behavior
- **Error Handling**: Robust error handling and fallback mechanisms
- **Rate Limiting**: Built-in rate limiting to respect API quotas

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

For permanent setup, add this to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Verify Installation

Run the test script to verify everything is working:

```bash
python test_ai_tools.py
```

## Usage

### Basic Usage

```python
from vendor.ai_tools import get_ai_description

# Dictionary mapping PDF paths to extracted text content
text_dict = {
    "/path/to/document1.pdf": "extracted text content...",
    "/path/to/document2.pdf": "more extracted text..."
}

# Generate descriptions
summary, descriptions = get_ai_description(text_dict)

print(f"Overall Summary: {summary}")
for pdf_path, description in descriptions.items():
    print(f"{pdf_path}: {description}")
```

### Integration with generate_text.py

The module is already integrated with your existing `generate_text.py` script. When you run:

```bash
python bin/generate_text.py --html_root_dir /path/to/html --doc_htmldir /docs --text_template_path /path/to/template --text_output_path /path/to/output --input_dir /path/to/input
```

The script will automatically:
1. Extract text from PDF files
2. Generate AI descriptions for each PDF
3. Include these descriptions in the generated HTML

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model to use for generation |
| `MAX_TEXT_LENGTH` | `8000` | Maximum characters to process per PDF |
| `MAX_TOKENS_PER_DESCRIPTION` | `150` | Maximum tokens per description |
| `TEMPERATURE` | `0.1` | Creativity level (lower = more consistent) |
| `TIMEOUT_SECONDS` | `30` | API request timeout |
| `REQUESTS_PER_MINUTE` | `60` | Rate limiting |
| `DELAY_BETWEEN_REQUESTS` | `1.0` | Delay between requests |

### Model Selection

- **`gpt-4o`**: Most capable, highest cost
- **`gpt-4o-mini`**: Good balance of capability and cost (recommended)
- **`gpt-3.5-turbo`**: Fastest, lowest cost, good for simple tasks

## How It Works

### 1. Text Extraction
The system extracts text from the first few pages of each PDF using PyMuPDF.

### 2. Content Analysis
For each PDF, the AI model analyzes the extracted text to identify:
- Main topic/subject area
- Document type (homework, notes, paper, etc.)
- Key mathematical concepts and topics
- Academic level and sophistication

### 3. Description Generation
The AI generates concise, accurate descriptions following strict guidelines:
- Single sentence format
- Factual and content-based
- Academic language appropriate for the field
- Consistent terminology and style

### 4. Quality Control
- Low temperature (0.1) ensures consistency
- Token limits prevent overly long descriptions
- Error handling for failed extractions or API calls

## Example Output

### Input PDFs
- `ma5204_hw1.pdf` - Linear algebra homework
- `complex_analysis_ahlfors.pdf` - Complex analysis textbook
- `algebraic_geometry_hartshorne.pdf` - Algebraic geometry reference

### Generated Descriptions
```
Overall Summary: This collection contains 3 documents: ma5204_hw1, complex_analysis_ahlfors, and algebraic_geometry_hartshorne.

Individual Descriptions:
ma5204_hw1.pdf: Linear algebra homework assignment covering eigenvalues, eigenvectors, and linear transformations.
complex_analysis_ahlfors.pdf: Complex analysis textbook chapter on complex numbers, functions, and Cauchy-Riemann equations.
algebraic_geometry_hartshorne.pdf: Algebraic geometry reference text discussing schemes, sheaves, and Zariski topology.
```

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   ❌ OPENAI_API_KEY environment variable is not set
   ```
   Solution: Set the environment variable as described in installation.

2. **API Connection Failed**
   ```
   ❌ OpenAI API connection failed
   ```
   Solution: Check your internet connection and API key validity.

3. **Import Errors**
   ```
   DEBUG: import ai_tools failed
   ```
   Solution: Ensure the vendor directory is in your Python path.

4. **Rate Limiting**
   ```
   Rate limit exceeded
   ```
   Solution: Increase `DELAY_BETWEEN_REQUESTS` or reduce `REQUESTS_PER_MINUTE`.

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export LOG_LEVEL=DEBUG
```

## Cost Considerations

- **GPT-4o-mini**: ~$0.00015 per 1K input tokens, ~$0.0006 per 1K output tokens
- **Typical cost per PDF**: $0.001 - $0.005 depending on text length
- **Batch processing**: Process multiple PDFs together to optimize costs

## Performance Tips

1. **Batch Processing**: Process multiple PDFs in one call when possible
2. **Text Truncation**: The system automatically truncates very long texts to stay within limits
3. **Caching**: Consider implementing caching for repeated descriptions
4. **Parallel Processing**: For large collections, process PDFs in parallel batches

## Contributing

To improve the system:

1. **Prompt Engineering**: Modify prompts in `ai_tools.py` for better descriptions
2. **Model Selection**: Test different models for your specific use case
3. **Error Handling**: Add more robust error handling for edge cases
4. **Caching**: Implement local caching to reduce API calls

## License

This module is part of your personal website project. Use responsibly and in accordance with OpenAI's terms of service.
