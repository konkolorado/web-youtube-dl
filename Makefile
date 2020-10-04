.PHONY: help

define HELPTEXT
Please use "make <target>" where <target> is one of
 help:   to print this message
 test:   to run the full suite of tests
endef
export HELPTEXT

help:
	@echo "$$HELPTEXT"

test:
	poetry run pytest --cov=web_youtube_dl