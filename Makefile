.DEFAULT_GOAL := all

all : build blueprint

build:
	(lake -Kenv=dev update -R && lake -Kenv=dev exe cache get && lake -Kenv=dev build && lake -Kenv=dev build DemoProject:docs)

blueprint:
	(cd blueprint && inv all)

