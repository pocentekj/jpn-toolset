.PHONY: all format lint typecheck test

all: format lint typecheck

format:
	@ruff format

lint:
	@ruff check

typecheck:
	@pyright

test:
	@coverage run
	@coverage report
