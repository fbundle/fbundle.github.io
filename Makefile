
# =============================================================================
# Personal Website Build System Makefile
# =============================================================================
# This Makefile orchestrates the build process for a personal academic website
# that combines LaTeX documents, HTML pages, and TypeScript components.
#
# Build Process Overview:
# 1. vitae: Convert LaTeX CV to HTML using make4ht
# 2. pages: Generate HTML pages from templates and content
# 3. public_doc: Copy academic documents to web assets
# 4. text: Generate text posts from academic documents
# 5. javascript: Compile TypeScript to JavaScript
#
# Author: Khanh
# Repository: fbundle.github.io
# =============================================================================

# =============================================================================
# Configuration Variables
# =============================================================================

# Temporary directory for build artifacts
TMP_DIR := tmp

# Vitae (CV) Configuration
# Input: LaTeX source file for CV
VITAE_INPUT_PATH := /Users/khanh/mathdoc/vitae/main.tex
# Output: Directory where HTML CV will be generated
VITAE_OUTPUT_DIR := docs/assets/vitae

# HTML Pages Configuration
# Input: Source directory containing page content
PAGES_INPUT_DIR := src/pages
# Output: Directory where generated HTML pages will be placed
PAGES_OUTPUT_DIR := docs/pages
# Template: Base HTML template for page generation
PAGES_TEMPLATE_PATH := src/template.html

# Public Documents Configuration
# Root directory for all HTML output
HTML_ROOT_DIR := docs
# Web path for public documents (relative to HTML root)
PUBLIC_DOC_HTMLDIR := /assets/public_doc
# Input: Local directory containing academic documents to publish
PUBLIC_DOC_INPUT_PATH := /Users/khanh/mathdoc/public_doc
# Output: Calculated output directory for public documents
PUBLIC_DOC_OUTPUT_DIR := $(dir $(HTML_ROOT_DIR)$(PUBLIC_DOC_HTMLDIR:%/=%))

# Text Posts Configuration
# Template for generating text post pages
TEXT_TEMPLATE_PATH := docs/pages/posts/text.template.html
# Output file for generated text posts
TEXT_OUTPUT_PATH := docs/pages/posts/text.html

# JavaScript Configuration
# Input: TypeScript source file
TS_INPUT_PATH := src/post-script.ts
# Output: Directory for compiled JavaScript files
JS_OUTPUT_DIR := docs/js

# =============================================================================
# Build Targets
# =============================================================================

# Default target: build all components
all: vitae pages text javascript

# =============================================================================
# Individual Build Targets
# =============================================================================

# Generate HTML CV from LaTeX source
# Uses make4ht (Make4HT) to convert LaTeX to HTML with styling
# - Creates output directory if it doesn't exist
# - Uses temporary build directory to avoid cluttering source
vitae:
	@echo "Generating HTML CV from LaTeX source..."
	make4ht \
  		--output-dir $(VITAE_OUTPUT_DIR) \
  		--build-dir $(TMP_DIR) \
  		$(VITAE_INPUT_PATH)
	@echo "CV generation complete: $(VITAE_OUTPUT_DIR)"

# Generate HTML pages from templates and content
# Uses Python script to process page templates and generate static HTML
# - Processes all files in PAGES_INPUT_DIR
# - Applies template from PAGES_TEMPLATE_PATH
# - Outputs to PAGES_OUTPUT_DIR
pages:
	@echo "Generating HTML pages from templates..."
	python bin/generate_pages.py \
		--input_dir $(PAGES_INPUT_DIR) \
		--output_dir $(PAGES_OUTPUT_DIR) \
		--template $(PAGES_TEMPLATE_PATH)
	@echo "Page generation complete: $(PAGES_OUTPUT_DIR)"

# Copy academic documents to web assets directory
# Uses rsync to efficiently sync documents with the following options:
# -a: archive mode (preserves permissions, timestamps, etc.)
# -v: verbose output
# -h: human-readable file sizes
# --delete: remove files in destination that don't exist in source
# --progress: show progress during transfer
public_doc:
	@echo "Copying academic documents to web assets..."
	rsync -avh --delete --progress \
		$(PUBLIC_DOC_INPUT_PATH) \
		$(PUBLIC_DOC_OUTPUT_DIR)
	@echo "Document copying complete: $(PUBLIC_DOC_OUTPUT_DIR)"

# Generate text posts from academic documents
# Depends on: pages, public_doc (must run after these targets)
# Uses Python script to create blog-style text posts from academic papers
# - Processes documents in the public_doc directory
# - Generates metadata and descriptions
# - Creates formatted HTML posts
text: pages public_doc
	@echo "Generating text posts from academic documents..."
	python bin/generate_text.py \
		--html_root_dir $(HTML_ROOT_DIR) \
		--doc_htmldir $(PUBLIC_DOC_HTMLDIR) \
		--text_template_path $(TEXT_TEMPLATE_PATH) \
		--text_output_path $(TEXT_OUTPUT_PATH)
	@echo "Text post generation complete: $(TEXT_OUTPUT_PATH)"

# Compile TypeScript to JavaScript
# Uses TypeScript compiler with modern ES2020 target
# - --target ES2020: Use ES2020 JavaScript features
# - --module ES2020: Use ES2020 module system
# - --strict: Enable strict type checking
# - --outDir: Specify output directory for compiled files
javascript:
	@echo "Compiling TypeScript to JavaScript..."
	tsc $(TS_INPUT_PATH) --outDir $(JS_OUTPUT_DIR) --target ES2020 --module ES2020 --strict
	@echo "TypeScript compilation complete: $(JS_OUTPUT_DIR)"

# =============================================================================
# Utility Targets
# =============================================================================

# Clean up all generated files and directories
# Removes temporary files and all build outputs
# Use this before a fresh build to ensure clean state
clean:
	@echo "Cleaning up build artifacts..."
	rm -rf $(TMP_DIR)
	rm -rf $(VITAE_OUTPUT_DIR)
	rm -rf $(PAGES_OUTPUT_DIR)
	rm -rf $(JS_OUTPUT_DIR)
	@echo "Cleanup complete"

# Force rebuild all targets (clean + all)
# Useful when you want to ensure a completely fresh build
rebuild: clean all

# =============================================================================
# Help Target
# =============================================================================

# Display available targets and their descriptions
help:
	@echo "Available targets:"
	@echo "  all        - Build all components (default)"
	@echo "  vitae      - Generate HTML CV from LaTeX"
	@echo "  pages      - Generate HTML pages from templates"
	@echo "  public_doc - Copy academic documents to web assets"
	@echo "  text       - Generate text posts from academic documents"
	@echo "  javascript - Compile TypeScript to JavaScript"
	@echo "  clean      - Remove all generated files"
	@echo "  rebuild    - Clean and rebuild everything"
	@echo "  help       - Show this help message"

# Make 'help' the default target when no target is specified
.DEFAULT_GOAL := help



