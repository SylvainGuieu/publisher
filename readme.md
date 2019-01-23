Publisher helps to build a repository (local or remote) for pandoc tools to automatically build project related documents. 

Install
======= 
Short story: 

- edit the `config.yaml` file
- `python configure.py`
- ./install

To build the publisher you can populate:

- img/ folder to images
- src/ to other document to include as footer, header
- templates/valid pandoc templates
- css/  css used by pandoc 
- md/ *.md files used to include in any documents (mdfooter or mdheaders)

Also if the publisher repository is public you may want to edit the `tpl/index.md` file which will be the `index.html`



