import os


html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Khanh Nguyen</title>
    <link rel="stylesheet" href="/css/styles.css">
</head>
<body>
    <div class="container">
        <div class="include" url="/include/left-panel.html"></div>
        <div id="highlight" name="index"></div>
        <div class="main-content">
            <h1> Public PDFs </h1>
            {content}
            <div class="include" url="/include/footer.html"></div>
        </div>
    </div>
    <script src="/js/post-script.js"></script>
</body>
</html>

"""

dst_dir = "docs/build_out/pdf"
if __name__ == "__main__":
    item_list = []
    for name in os.listdir(dst_dir):
        item_list.append(f"<li> <a href=\"/build_out/pdf/{name}\">{name}</a> </li>")
    
    content = f"<ul>\n{'\n'.join(item_list)}\n</ul>"

    html = html_template.format(content=content)

    with open(f"{dst_dir}/index.html", "w") as f:
        f.write(html)



