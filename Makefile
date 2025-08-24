
TMP_DIR="tmp"
VITAE_INPUT_PATH="/Users/khanh/mathdoc/public_doc/vitae/main.tex"
VITAE_OUTPUT_DIR="docs/assets/vitae"

PAGES_INPUT_DIR="src/pages"
PAGES_OUTPUT_DIR="docs/pages"
PAGES_TEMPLATE_PATH="src/template.html"

HTML_ROOT_DIR="docs"
PUBLIC_DOC_HTMLDIR="/assets/public_doc"
PUBLIC_DOC_INPUT_DIR="/Users/khanh/mathdoc/public_doc"

TEXT_TEMPLATE_PATH="docs/pages/posts/text.template.html"
TEXT_OUTPUT_PATH="docs/pages/posts/text.html"

all: vitae pages text

run:
	go run bin/fileserver.go docs

vitae:
	# generate vitae
	make4ht \
  		--output-dir $(VITAE_OUTPUT_DIR) \
  		--build-dir $(TMP_DIR) \
  		$(VITAE_INPUT_PATH)

pages:
	# generate pages
	python bin/generate_pages.py \
		--input_dir $(PAGES_INPUT_DIR) \
		--output_dir $(PAGES_OUTPUT_DIR) \
		--template $(PAGES_TEMPLATE_PATH)

public_doc:
	# copy public_doc
	python bin/copy_public_doc.py \
		--html_root_dir $(HTML_ROOT_DIR) \
		--doc_htmldir $(PUBLIC_DOC_HTMLDIR) \
		--input_dir $(PUBLIC_DOC_INPUT_DIR)

text: pages public_doc
	# generate text
	python bin/generate_text.py \
		--html_root_dir $(HTML_ROOT_DIR) \
		--doc_htmldir $(PUBLIC_DOC_HTMLDIR) \
		--text_template_path $(TEXT_TEMPLATE_PATH) \
		--text_output_path $(TEXT_OUTPUT_PATH)


clean:
	rm -rf $(TMP_DIR)
	rm -rf $(VITAE_OUTPUT_DIR)
	rm -rf $(PAGES_OUTPUT_DIR)



