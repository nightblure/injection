test:
	hatch test --cover --all --randomize

test3.8:
	hatch test -i python="3.8" --cover --randomize

test-py:
	hatch test -i python="$(v)" --cover --randomize

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
	pdm run mypy src tests
