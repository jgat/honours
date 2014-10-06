all: thesis.pdf

clean:
	rm *.aux *.log *.toc *.pdf

thesis.pdf: thesis.tex src/*.tex src/*/*.tex
	pdflatex thesis.tex
	pdflatex thesis.tex
