### Common Lisp CommunitySpec

(name t.b.d)

This project aims to provide an alternative to the Common Lisp HyperSpec.
Due to its license, the HyperSpec can not be modified in any way, so this project 
is using a rendition of the ANSI Common Lisp specification made by Bill Schelter [(see the emacswiki for more information)](https://www.emacswiki.org/emacs/CommonLispHyperspec). 

The files are in [.info](https://www.gnu.org/software/texinfo/manual/texinfo/html_node/Info-Files.html) format. Each file contains one or more "nodes", which are output as
a HTML file each.
For the conversion, a python script (`convert.py`) is used to read in the .info files,
extracting all contained nodes, and  writing each node into an intermediate .json file.
Since the nodes are referenced by their names throughout the spec, the filenames are the MD5 hashes of the node names, this avoids any problems with non-allowed characters in URLs. 
The JSON files are read in again and for each file, an HTML file is generated.
The generated files can be found at `/output`.

It should be emphasized that the conversion script is the product of a few busy mornings and quite messy.
The aim would be to arrive at a HTML output that correctly formatted most of the specification's content, and the leave the rest for manual correction in the HTML files themselves.

