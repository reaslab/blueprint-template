.DEFAULT_GOAL := all

PROJECT = DemoProject

.PHONY: all build blueprint blueprint-dev analyze serve update

all : build blueprint

build:
	(lake exe cache get && lake build && DOCGEN_SRC="vscode" lake build ${PROJECT}:docs)

build-print:
	(cd blueprint && mkdir -p print && cd src && xelatex -output-directory=../print print.tex)
	(cd blueprint/print && BIBINPUTS=../src bibtex print.aux)
	(cd blueprint/src && xelatex -output-directory=../print print.tex)
	(cd blueprint/src && xelatex -output-directory=../print print.tex)
	(cp blueprint/print/print.bbl blueprint/src/web.bbl)

build-web:
	(cd blueprint/src && poetry run plastex -c plastex.cfg web.tex)

blueprint: build build-print build-web
	(cd blueprint && cp -r ../.lake/build/doc ./web/)

blueprint-dev: build-print build-web
	(cd blueprint/web && poetry run python -m http.server)

analyze:
	(poetry run python3 blueprint/blueprint_auto.py -p ${PROJECT})
