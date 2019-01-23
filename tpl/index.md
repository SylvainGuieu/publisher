---
title: "Publisher"
author: ""
---

This is the default Readme for publisher. You may want to edit your own in 
    
    tpl/index.md 

Tells brief summary of publisher capabilities.

To create a nice standardized markdown document this is quit simple. 
Download this <a href="Makefile">Makefile</a> copy it to the directory where your markdown files 
are and execute `make`.
    
    >> curl {{ urlRoot }}/Makefile > Makefile
    >> make html 

This will create html files for all the `*.md` and `*.pmd` files. `*.pmd` are for [pweave]. The output goes inside the `output` directory, created if needed.
    
You can create different kind of documents by providing a pre-extention before the `.md`
Valid extension are: 
{% for kind in conf['pandoc']['kinds']['custom'] %}
*.{{ kind['ext'] }}
: {{ kind['description'] }}

{% endfor %}


Requirement
----------- 
The only mandatory requirement is to have [pandoc] installed. However: 

- If the directory contains *.pmv files, [pweave] will be needed.
- if the make target is hpdf: [wkhtmltopdf] is needed. `make hpdf` will create a pdf toward a html file contrary to `make pdf` which will create a pdf from LaTeX. 
 






  
