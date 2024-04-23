.DEFAULT_GOAL := all

all : build blueprint

build:
	(lake -Kenv=dev update && lake -Kenv=dev exe cache get && lake -Kenv=dev build)

blueprint:
	(cd blueprint && inv all)

