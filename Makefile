.PHONY: full clean

all: thesis.pdf ch1.pdf ch2.pdf ch3.pdf talk.pdf handout.pdf

full:
	$(MAKE) -B thesis.pdf ch1.pdf ch2.pdf ch3.pdf talk.pdf handout.pdf
	$(MAKE) -B thesis.pdf ch1.pdf ch2.pdf ch3.pdf talk.pdf handout.pdf
	$(MAKE) -B ch1.pdf ch2.pdf ch3.pdf

clean:
	rm *.log *.toc *.pdf *.aux */*.aux *.nav *.out *.snm
	rm src/appendix/{hypergraphs,check,decompositions}.tex

thesis.pdf: thesis.tex src/*.tex src/*/*.tex src/appendix/hypergraphs.tex src/appendix/check.tex src/appendix/decompositions.tex
	pdflatex thesis.tex

ch1.pdf: thesis.tex src/introduction.tex src/introduction/*.tex
	pdflatex -jobname=ch1 "\includeonly{src/introduction}\input{thesis}"

ch2.pdf: thesis.tex src/hypergraph-designs.tex src/hypergraph-designs/*.tex
	pdflatex -jobname=ch2 "\includeonly{src/hypergraph-designs}\input{thesis}"

ch3.pdf: thesis.tex src/methods.tex src/methods/*.tex
	pdflatex -jobname=ch3 "\includeonly{src/methods}\input{thesis}"

src/appendix/hypergraphs.tex: code/hypergraphs.py
	echo '\\begin{verbatim}' > src/appendix/hypergraphs.tex
	cat code/hypergraphs.py >> src/appendix/hypergraphs.tex
	echo '\\end{verbatim}' >> src/appendix/hypergraphs.tex

src/appendix/check.tex: code/check.py
	echo '\\begin{verbatim}' > src/appendix/check.tex
	cat code/check.py >> src/appendix/check.tex
	echo '\\end{verbatim}' >> src/appendix/check.tex

src/appendix/decompositions.tex: code/decompositions.py
	echo '\\begin{verbatim}' > src/appendix/decompositions.tex
	cat code/decompositions.py >> src/appendix/decompositions.tex
	echo '\\end{verbatim}' >> src/appendix/decompositions.tex

talk.pdf: src/talk.tex src/slides.tex
	pdflatex src/talk.tex

handout.pdf: src/handout.tex src/slides.tex
	pdflatex src/handout.tex
