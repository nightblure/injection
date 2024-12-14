# Contributing

Injection is an open source solution, so any suggestions and suggestions are welcome.
You can describe [bug reports and errors](https://github.com/nightblure/injection/issues)
in the project release, and also send [merge requests](https://github.com/nightblure/injection/pulls)
with fixes and new features!

Modern packages, dependencies and practices were used in the development of the Injection:
* linter and formatter - [Ruff](https://docs.astral.sh/ruff/);
* type checking - [mypy](https://github.com/python/mypy);
* package manager - [uv](https://github.com/astral-sh/uv);
* package builder - [Hatch](https://github.com/pypa/hatch);
* testing - [pytest](https://github.com/pytest-dev/pytest);
* assembly and documentation management - [Sphinx](https://www.sphinx-doc.org/en/master/).

The following will describe some useful steps for local development:
* to install dependencies, use the command `make deps`;
* to run the tests, use the command `make test`;
* to start pre-commit hooks and linter, use the command `make lint`;
* to install dependencies for the documentation server, use the command `make docs-deps`;
* to start the server with documentation locally, use the command `make docs-server`.
