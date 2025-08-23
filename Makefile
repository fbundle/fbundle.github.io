

all: vitae pages text

run:
	go run bin/fileserver.go docs

vitae:
	# generate vitae
	make4ht \
  		--output-dir "docs/assets/vitae" \
  		--build-dir "tmp" \
  		"/Users/khanh/mathdoc/public_doc/vitae/main.tex"

pages:
	# generate pages
	python bin/generate_pages.py \
		--input_dir "src/pages" \
		--output_dir "docs/pages" \
		--template "src/template.html"

text: pages
	# generate public_doc text
	python bin/generate_text.py \
		--html_root_dir "docs" \
		--doc_htmldir "/assets/public_doc" \
		--text_template_path "docs/pages/posts/text.template.html" \
		--text_output_path "docs/pages/posts/text.html" \
		--input_dir "/Users/khanh/mathdoc/public_doc"


clean:
	rm -rf "tmp"
	rm -rf "docs/assets/vitae"
	rm -rf "docs/pages"
	rm -rf "docs/assets/public_doc"



