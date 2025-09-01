
TMP_DIR := tmp
VITAE_INPUT_PATH := /Users/khanh/mathdoc/public_doc/uncategorized/vitae/main.tex
VITAE_OUTPUT_DIR := docs/assets/vitae

PAGES_INPUT_DIR := src/pages
PAGES_OUTPUT_DIR := docs/pages
PAGES_TEMPLATE_PATH := src/template.html


HTML_ROOT_DIR := docs
PUBLIC_DOC_HTMLDIR := /assets/public_doc
PUBLIC_DOC_INPUT_PATH := /Users/khanh/mathdoc/public_doc
PUBLIC_DOC_OUTPUT_DIR := $(dir $(HTML_ROOT_DIR)$(PUBLIC_DOC_HTMLDIR:%/=%))

PUBLIC_DOC_DESC_PATH=data/public_doc_desc.json
TEXT_TEMPLATE_PATH=docs/pages/posts/text.template.html
TEXT_OUTPUT_PATH=docs/pages/posts/text.html

TS_INPUT_PATH=src/post-script.ts
JS_OUTPUT_DIR=docs/js

all: vitae pages text javascript

run:
	go run bin/fileserver.go docs

ai_desc:
	# generate ai description
	python bin/generate_desc.py \
		--html_root_dir $(HTML_ROOT_DIR) \
		--doc_htmldir $(PUBLIC_DOC_HTMLDIR) \
		--desc_output_path $(PUBLIC_DOC_DESC_PATH)

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
	rsync -avh --delete --progress \
		$(PUBLIC_DOC_INPUT_PATH) \
		$(PUBLIC_DOC_OUTPUT_DIR)

text: pages public_doc
	# generate text
	python bin/generate_text.py \
		--html_root_dir $(HTML_ROOT_DIR) \
		--doc_htmldir $(PUBLIC_DOC_HTMLDIR) \
		--desc_input_path $(PUBLIC_DOC_DESC_PATH) \
		--text_template_path $(TEXT_TEMPLATE_PATH) \
		--text_output_path $(TEXT_OUTPUT_PATH)

javascript:
	# compile ts to js
	tsc $(TS_INPUT_PATH) --outDir $(JS_OUTPUT_DIR) --target ES2020 --module ES2020 --strict

clean:
	rm -rf $(TMP_DIR)
	rm -rf $(VITAE_OUTPUT_DIR)
	rm -rf $(PAGES_OUTPUT_DIR)
	rm -rf $(JS_OUTPUT_DIR)



