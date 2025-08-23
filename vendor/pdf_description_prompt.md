# PDF Description Generation Prompt Specification

## Task Overview
Generate accurate, concise descriptions of academic PDF documents based on extracted text content. The descriptions should help users quickly understand what each document contains without having to open it.

## Input Format
- **Document Name**: The filename of the PDF (e.g., "ma5204_hw1.pdf", "complex_analysis_ahlfors.pdf")
- **Text Content**: Extracted text from the first few pages of the PDF document

## Output Requirements

### Description Format
Each description should be a **single, clear sentence** that captures the essence of the document.

### Content Requirements
1. **Main Topic/Subject Area**: Identify the primary academic discipline or field
2. **Document Type**: Specify whether it's homework, notes, a paper, assignment, etc.
3. **Key Concepts**: Mention important mathematical concepts, theorems, or topics covered
4. **Accuracy**: Ensure the description is factual and based on the provided content
5. **Conciseness**: Keep descriptions to 2-3 sentences maximum

### Examples of Good Descriptions
- "Linear algebra homework assignment covering eigenvalues, eigenvectors, and diagonalization problems."
- "Complex analysis course notes on Cauchy's integral theorem, residue theory, and contour integration."
- "Algebraic geometry paper discussing sheaf theory, cohomology, and the Künneth theorem."
- "Differential equations assignment on solving first-order linear equations and separation of variables."

### Examples of Poor Descriptions
- ❌ "A math document with equations and stuff." (Too vague)
- ❌ "This is about calculus and has problems to solve." (Too generic)
- ❌ "Complex mathematical concepts and advanced theories." (Not specific enough)

## Quality Guidelines

### Accuracy
- Base descriptions solely on the provided text content
- Do not infer or assume content not present in the text
- If text is unclear or insufficient, note this in the description

### Consistency
- Use consistent terminology across similar document types
- Maintain similar length and detail level for comparable documents
- Follow academic writing conventions

### Clarity
- Use precise, academic language
- Avoid jargon unless it's clearly defined in the context
- Make descriptions understandable to students and researchers in the field

## Error Handling
- If text extraction fails or content is empty, return "No text content available"
- If content is corrupted or unreadable, note this in the description
- Handle mathematical notation and symbols appropriately

## Technical Constraints
- Maximum response length: 150 tokens
- Temperature: 0.1 (for consistency)
- Model: GPT-4o-mini (default) or as specified
- Timeout: 30 seconds per document

## Special Considerations for Academic Documents

### Mathematical Content
- Recognize common mathematical notation and symbols
- Identify mathematical concepts even when described in text
- Note the level of mathematical sophistication (e.g., undergraduate, graduate)

### Course Materials
- Distinguish between different types of course materials
- Note course codes when present (e.g., MA5204, MA5216)
- Identify whether content is from lectures, tutorials, or assignments

### Research Papers
- Identify research topics and methodologies
- Note if it's a review paper, original research, or survey
- Mention key authors or references if significant

## Testing and Validation
- Test with various document types to ensure consistency
- Validate descriptions against actual document content
- Monitor for accuracy and relevance in generated descriptions
