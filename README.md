### Common Lisp CommunitySpec

This project aims to provide an alternative to the [Common Lisp HyperSpec](http://www.lispworks.com/documentation/HyperSpec/Front/index.htm).
Due to its license, the HyperSpec cannot be modified in any way, so this project 
is using a rendition of the ANSI Common Lisp specification draft, which is available in `.info` or `.tex` format on various locations.

A more or less recent live version of the repository can be found at [cl-community-spec.github.io](https://cl-community-spec.github.io)

For the syntax highlighting, [orthecreedence/highlight-lisp](https://github.com/orthecreedence/highlight-lisp) is used.

PRs welcome!

### Note for contributing

The initial HTML pages have been generated using `texi2any` on the specifiction's `.texi` files. In the following, `convert.py` and other Python scripts you can find in
the repository have been used to improve/cleanup that generated HTML. Now the output is at a point where it IMO makes more sense to just do the changes directly on the HTML instead 
of going through the conversion scripts, so if you want to contribute, I suggest just making your changes on the files in `pages/`. 

One thing though: please run `backlinks.py` after you made any changes that alter the title 
of a page or any links in the page, as that script generates the `Backlinks` section on each page.
The generated HTML is kind of messy, but please be careful with auto-formatting tools. A lot of the HTML is preformatted, and not all of the
preformatted text sits inside `<pre></pre>` tags yet.
