test:
	hatch test --cover --all --randomize

test-ci:
	pdm run pytest -rA tests --cov=src --cov-report term-missing --cov-report=xml --asyncio-mode=auto

lint:
	pdm run pre-commit install
	pdm run pre-commit run --all-files

lint-ci:
	pre-commit install && pre-commit run --color=always --all-files

deps:
	pdm install

build:
	rm -r -f dist && pdm run hatch build

hatch-env-prune:
	pdm run hatch env prune

docs-server:
	rm -rf docs/build
	pdm run sphinx-autobuild docs docs/build

build-docs:
	rm -rf docs/build/* && rm -rf docs/build/{*,.*}
	pdm run sphinx-build docs docs/build

# https://pdm-project.org/latest/usage/dependency/#select-a-subset-of-dependency-groups-to-install
docs-deps:
	pdm install -G docs

# example: make tag v="v3.9.2", TAG MUST INCLUDE v
tag:
	pdm run hatch version "${v}"
	git tag -a ${v} -m "${v}"

release:
	git add . && git commit -m "Bump version" && git push origin $(git describe --tags $(git rev-list --tags --max-count=1))

mypy:
	pdm run mypy src
