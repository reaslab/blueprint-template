.DEFAULT_GOAL := all

PROJECT = ./DemoProject

all : build blueprint

.PHONY: all build blueprint

build:
	(lake -Kenv=dev update -R && lake -Kenv=dev exe cache get && lake -Kenv=dev build && lake -Kenv=dev build DemoProject:docs)

blueprint:
	(cd blueprint && inv all)

analyze:
	(python3 blueprint/blueprint_auto.py -p ${PROJECT})

serve: blueprint
	(cd blueprint/web && python3 -m http.server)