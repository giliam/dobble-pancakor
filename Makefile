# Makefile
# 
# Converts Markdown to other formats (HTML, PDF, DOCX, RTF, ODT, EPUB) using Pandoc
# <http://johnmacfarlane.net/pandoc/>
# source : https://gist.github.com/kristopherjohnson/7466917
#
# Run "make" (or "make all") to convert to all other formats
#
# Run "make clean" to delete converted files

# Convert all files in this directory that have a .md suffix
SOURCE_DOCS := $(wildcard docs/*.md)

EXPORTED_DOCS=\
 $(SOURCE_DOCS:.md=.html) \
 $(SOURCE_DOCS:.md=.pdf)

PANDOC=pandoc
PDFLATEX=pdflatex

-include path.mk

PANDOC_OPTIONS=-s --number-sections --toc

PANDOC_HTML_OPTIONS=--mathjax
PANDOC_PDF_OPTIONS=--pdf-engine=$(PDFLATEX)

# Pattern-matching Rules

%.html : %.md
	$(PANDOC) $(PANDOC_OPTIONS) $(PANDOC_HTML_OPTIONS) -o $@ $<

%.pdf : %.md
	$(PANDOC) $(PANDOC_OPTIONS) $(PANDOC_PDF_OPTIONS) -o $@ $<

# Targets and dependencies

.PHONY: docs clean

docs : $(EXPORTED_DOCS)

clean: 
	- rm $(EXPORTED_DOCS)