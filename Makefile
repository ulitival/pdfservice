.PHONY: setup init update test lint mypy check build clean clean_db

setup:
	pyenv install --verbose --skip-existing
	pyenv local
	poetry config virtualenvs.in-project true

init:
	poetry install

update:
	poetry update --lock
	poetry install

test:
	poetry run pytest --verbose --color=yes --junit-xml=tests/results.xml -o junit_family=xunit1 --cov-report xml:tests/coverage.xml --cov=.

lint:
	poetry run pylint --exit-zero pdf_rendering_service -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > sonar-result

mypy:
	poetry run mypy pdf_rendering_service --no-strict-optional --ignore-missing-imports  --junit-xml=tests/mypy.xml

check: test mypy lint
	cat sonar-result

build:
	poetry build
	poetry export -f requirements.txt --output requirements.txt --without-hashes

clean:
	rm -rf .mypy_cache .pytest_cache tests/*.xml .coverage sonar-result dist requirements.txt

clean_db:
	rm -r .docker/data/postgresql/data/*