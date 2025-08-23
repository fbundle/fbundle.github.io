# Advanced Prompt Engineering for PDF Description Generation

## Core Prompt Structure

The current prompt follows this structure:

```
You are an expert academic document analyzer. Your task is to provide a concise, accurate description of the following document.

Document: {document_name}
Content: {extracted_text}

Please provide a description that:
1. Identifies the main topic/subject area
2. Specifies the document type (e.g., homework, notes, paper, assignment)
3. Mentions key mathematical concepts, theorems, or topics covered
4. Is concise (2-3 sentences maximum)
5. Is accurate and factual based on the content provided

Format your response as a single, clear sentence that captures the essence of the document.
```

## Prompt Optimization Strategies

### 1. Role Definition
**Current**: "You are an expert academic document analyzer"
**Alternatives**:
- "You are a mathematics professor specializing in document classification"
- "You are a research librarian with expertise in academic materials"
- "You are an AI trained to extract key information from mathematical documents"

### 2. Task Specification
**Current**: "provide a concise, accurate description"
**Alternatives**:
- "generate a one-sentence summary that captures the document's essence"
- "create a brief, informative description suitable for academic catalogs"
- "extract the most important information and present it clearly"

### 3. Output Format
**Current**: "single, clear sentence"
**Alternatives**:
- "one concise sentence (maximum 25 words)"
- "brief description in academic catalog format"
- "summary suitable for document indexing"

## Enhanced Prompt Variations

### Version 1: Academic Catalog Style
```
You are a mathematics librarian creating catalog entries. Analyze this document and provide a one-sentence description that includes:
- Subject area (e.g., Linear Algebra, Complex Analysis)
- Document type (e.g., homework, lecture notes, research paper)
- Key topics or concepts mentioned
- Academic level if apparent

Document: {name}
Content: {text}

Format: Single sentence, academic tone, maximum 30 words.
```

### Version 2: Research Paper Abstract Style
```
You are a research assistant summarizing academic documents. For this document, provide a concise description that:
- Identifies the primary field of study
- Describes the content type and scope
- Mentions specific mathematical concepts, theorems, or methods
- Indicates the level of mathematical sophistication

Document: {name}
Content: {text}

Output: One sentence summary in research paper abstract style.
```

### Version 3: Student-Friendly Style
```
You are a helpful tutor explaining what's in this document. Create a clear, simple description that tells a student:
- What subject this document covers
- What type of material it contains (homework, notes, etc.)
- What main topics or concepts they'll learn about
- Whether it's beginner, intermediate, or advanced level

Document: {name}
Content: {text}

Response: One friendly, informative sentence.
```

## Context-Aware Prompts

### For Mathematical Documents
```
You are analyzing a mathematical document. Focus on:
- Mathematical field (Algebra, Analysis, Geometry, etc.)
- Specific concepts (e.g., eigenvalues, Cauchy-Riemann equations)
- Mathematical notation and symbols
- Proof techniques or problem-solving approaches

Document: {name}
Content: {text}

Provide a mathematical description in one sentence.
```

### For Course Materials
```
You are categorizing course materials. Identify:
- Course code if present (e.g., MA5204, MA5216)
- Material type (lecture notes, homework, tutorial, exam)
- Week or chapter information if available
- Specific topics covered

Document: {name}
Content: {text}

Format: "Course Code - Material Type - Topics" in one sentence.
```

### For Research Papers
```
You are analyzing a research paper. Extract:
- Research area and subfield
- Type of contribution (original research, survey, review)
- Key methodologies or approaches
- Main results or findings

Document: {name}
Content: {text}

Output: One sentence research summary.
```

## Quality Control Prompts

### Accuracy Verification
```
Before providing your description, verify:
1. All information is directly supported by the text
2. Mathematical concepts are correctly identified
3. Document type is accurately classified
4. No assumptions are made beyond the content

Document: {name}
Content: {text}

If uncertain about any aspect, note this in your description.
```

### Consistency Check
```
You are part of a system that analyzes many documents. Ensure your description:
- Uses consistent terminology with other descriptions
- Maintains similar detail level for comparable documents
- Follows the same format and style
- Is appropriate for the document's complexity level

Document: {name}
Content: {text}

Provide a consistent, well-structured description.
```

## Error Handling Prompts

### For Incomplete Content
```
If the extracted text is incomplete or unclear, your description should:
- Acknowledge the limitation
- Describe what can be determined
- Note any uncertainty
- Suggest what additional information would be helpful

Document: {name}
Content: {text}

Provide the best possible description given the available content.
```

### For Technical Issues
```
If you encounter technical problems or unclear content:
- Focus on what you can reliably identify
- Use general categories when specific details are unclear
- Maintain academic tone even with limited information
- Flag any significant uncertainties

Document: {name}
Content: {text}

Generate the most accurate description possible.
```

## Performance Optimization

### Token Efficiency
- Keep prompts concise but complete
- Use clear, direct instructions
- Avoid redundant requirements
- Focus on essential output criteria

### Consistency Improvements
- Use fixed templates for similar document types
- Maintain consistent terminology
- Apply uniform formatting rules
- Standardize quality standards

### Error Reduction
- Include validation steps in prompts
- Request confidence levels when appropriate
- Ask for clarification on ambiguous content
- Provide fallback strategies for edge cases

## Testing and Validation

### A/B Testing Prompts
1. Test different role definitions
2. Compare output formats
3. Evaluate consistency across documents
4. Measure accuracy against human judgments

### Quality Metrics
- Description accuracy
- Consistency across similar documents
- Completeness of information
- Readability and clarity
- Academic appropriateness

### Iterative Improvement
- Collect feedback on generated descriptions
- Identify common failure modes
- Refine prompts based on results
- Test with diverse document types

## Best Practices

1. **Start Simple**: Begin with basic prompts and add complexity gradually
2. **Test Extensively**: Validate prompts with various document types
3. **Monitor Quality**: Track performance metrics over time
4. **Iterate Carefully**: Make small changes and measure impact
5. **Document Changes**: Keep track of prompt modifications and their effects
6. **User Feedback**: Incorporate feedback from actual users
7. **Performance Tuning**: Balance accuracy with speed and cost

## Example Optimized Prompt

```
You are an expert mathematics document classifier. Analyze this document and provide a one-sentence description that includes:

REQUIRED ELEMENTS:
- Primary mathematical field (e.g., Linear Algebra, Complex Analysis)
- Document type (homework, notes, paper, assignment, tutorial)
- Key mathematical concepts or topics (2-3 specific items)
- Academic level if apparent (undergraduate/graduate)

DOCUMENT: {name}
CONTENT: {text}

OUTPUT FORMAT: Single sentence, academic tone, maximum 25 words.
QUALITY CHECK: Ensure all information is directly supported by the content.

Example format: "Linear algebra homework covering eigenvalues, eigenvectors, and linear transformations."
```
