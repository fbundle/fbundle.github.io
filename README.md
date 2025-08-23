## Hi there 👋

[fbundle.github.io](https://fbundle.github.io/)

[github.com/fbundle/fbundle.github.io](https://github.com/fbundle/fbundle.github.io)

## TODO

- instead of every page is of `template.html`, I can make every page be `page_name.content.html` and use python or js to wrap the necessary header and footer, for example `/pages/text.html` is just as below

```html
<div class="include" url="/include/before_content.html"></div>
<div class="include" url="/content/text.html"></div>
<div class="include" url="/include/after_content.html"></div>
```

or `content/text.html` is like


```html
{before_content}
<div> actual content </div>
{after_content}
```

then python will generate the full html `pages/text.html`