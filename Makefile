test:
	hatch test --cover --all --randomize

test3.8:
	hatch test -i python="3.8" --cover --randomize

test-py:
	hatch test -i python="$(v)" --cover --randomize

lint:
	pre-commit install
	pre-commit run --all-files

deps:
	uv sync

build:
	rm -rf dist && pdm run hatch build

hatch-env-prune:
	hatch env prune

docs-server:
	rm -rf docs/build
	sphinx-autobuild docs docs/build

build-docs:
	rm -rf docs/build/* && rm -rf docs/build/{*,.*}
	sphinx-build docs docs/build

# example: make tag v="v3.9.2", TAG MUST INCLUDE v
release:
	git add . && git commit -m "Bump version" && git push --force
	git tag -a "v$(hatch version)" -m "v$(hatch version)"
	git push --force origin "$(git describe --tags $(git rev-list --tags --max-count=1))"

release-patch:
	hatch version patch
	make release

release-minor:
	hatch version minor
	make release

mypy:
	mypy src tests
