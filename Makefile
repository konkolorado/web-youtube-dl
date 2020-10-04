.PHONY: help

define HELPTEXT
Please use "make <target>" where <target> is one of
 help:      to print this message
 test:      to run the full suite of tests
 compose:	to run the project as a Docker-compose app
 container: to build the project's containers
endef
export HELPTEXT

help:
	@echo "$$HELPTEXT"

test:
	poetry run pytest --cov=web_youtube_dl

container:
	docker build . -t  web-youtube-dl:latest --force-rm

compose:
	docker-compose up -d