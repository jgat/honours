.PHONY: full clean

all: thesis.pdf

full:
	$(MAKE) -B thesis.pdf ch1.pdf ch2.pdf ch3.pdf
	$(MAKE) -B thesis.pdf ch1.pdf ch2.pdf ch3.pdf
	$(MAKE) -B thesis.pdf ch1.pdf ch2.pdf ch3.pdf

clean:
	rm *.log *.toc *.pdf *.aux */*.aux

thesis.pdf: thesis.tex src/*.tex src/*/*.tex
	pdflatex thesis.tex

ch1.pdf: thesis.tex src/introduction.tex src/introduction/*.tex
	pdflatex -jobname=ch1 "\includeonly{src/introduction}\input{thesis}"

ch2.pdf: thesis.tex src/hypergraph-designs.tex src/hypergraph-designs/*.tex
	pdflatex -jobname=ch2 "\includeonly{src/hypergraph-designs}\input{thesis}"

ch3.pdf: thesis.tex src/methods.tex src/methods/*.tex
	pdflatex -jobname=ch3 "\includeonly{src/methods}\input{thesis}"
