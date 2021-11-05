install:
	poetry install

package-install:
	pip install --user dist/*.whl

test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=page_loader --cov-report xml

lint:
	poetry run flake8 page_loader

selfcheck:
	poetry check

check: selfcheck test lint

build: check
	poetry build

.PHONY: install test lint selfcheck check build