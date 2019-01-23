# publisher 0.9
# 
# do not remove the first line of this file it is used
# to iddentify a publisher Makefile
# Makefile
# 
# Converts Markdown to other formats (HTML, PDF, DOCX, RTF, ODT, EPUB) using Pandoc
# And convert Markdown -Pweave *.pmd file using pwave than Pandoc
#
# Run "make" (or "make all") to convert to pdf and html
#
# Run "make clean" to delete converted files
# Or run for individual formats
# make pdf
# make html
# make epub
# make md # if the source are *.pmd file 
# make rtf
# make docx

# Convert all files in this directory that have a .md or a .pmd suffix
# The converted files will be in the $(OUTPUT) directory. 

SOURCE= .
OUTPUT= output

RM=/bin/rm

dir_guard=@mkdir -p $(@D)
CURL=curl

{% if remote %}
src_dir_guard=@mkdir -p .pandoc
src_template_dir_guard=@mkdir -p .pandoc/templates
{% else %}
src_dir_guard=
{% endif %}

{% for guard in cmds['guards'] %}
{{ guard }}
{% endfor %}

# wkhtmltopdf --print-media-type
PANDOC=pandoc
PWEAVE=pweave
WKHTML=wkhtmltopdf


# MD Headers option for each outputs and kind 
{% for hdr in cmds['hdrs'] %}
{{ hdr }}
{% endfor %}

# MD Footers option for each outputs and kind 
{% for ftr in cmds['ftrs'] %}
{{ ftr }}
{% endfor %}

# MD optiona for each outputs and kind
{% for opt in cmds['opts'] %}
{{ opt }}
{% endfor %}

# static options 
PANDOC_OPTIONS=--smart --standalone
PWEAVE_OPTIONS=-f pandoc
WKHTML_OPTIONS=--print-media-type


#WKHTML_OPTIONS=
PANDOC_I_OPTIONS=--from markdown{% for p in pandoc['packages'] %}+{{ p }}{% endfor %}



{% for src in cmds['srcs'] %}
{{ src }}
{% endfor %}


PMD_TARGET_md= $(subst $(SOURCE)/, $(OUTPUT)/, $(SOURCE_PMD:.pmd=.md))
# targets for each output and kind 
{% for tgt in cmds['tgts'] %}
{{ tgt }}
{% endfor %}

# 
# Pattern-matching Rules


$(OUTPUT)/%.md : $(SOURCE)/%.pmd
	$(dir_guard)
	$(PWEAVE) $(PWEAVE_OPTIONS)  $< -o $@
# rules for each output and kind 
{% for rule in cmds['rules'] %}
{{ rule }}
{% endfor %}


# Targets and dependencies

.PHONY: all clean
{% for dep in cmds['deps'] %}
{{ dep }}
{% endfor %}

clean:
	- $(RM) -f $(OUTPUT)/*.html $(OUTPUT)/*.pdf $(OUTPUT)/*.docx $(OUTPUT)/*.rtf $(OUTPUT)/*.epub
	- $(RM) -rf $(OUTPUT)/figures 
	cmp -s $(SOURCE) $(OUTPUT); 	RETVAL=$$?; 	if [ $$RETVAL -eq 0 ]; then 				echo "Output is source"; 	else 