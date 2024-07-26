# Concepts and key features

With `Injection` you can implement the principle of Dependency Injection. This is needed for ...

Using this framework you can reduce [coupling](https://en.wikipedia.org/wiki/Coupling_(computer_programming))
and stop monkeypatching your tests.

The public API of this framework is almost completely identical to
[Dependency Injector](https://python-dependency-injector.ets-labs.org/index.html#),
because the author found it successful and understandable.
In addition, this will provide an easy migration to the current framework with
[Dependency Injector](https://python-dependency-injector.ets-labs.org/index.html#)
(see [migration from Dependency Injector](https://injection.readthedocs.io/latest/dev/migration-from-dependency-injector.html)).

## Features and advantages

* support **Python 3.8-3.12**;
* works with **FastAPI, Flask, Litestar** and **Django REST Framework**;
* dependency injection via `Annotated` in FastAPI;
* **no third-party dependencies**;
* **multiple containers**;
* providers - delegate object creation and lifecycle management to providers;
* **overriding** dependencies for tests without wiring;
* **100%** code coverage and very simple code;
* good [documentation](https://injection.readthedocs.io/latest/);
* intuitive and almost identical api with [dependency-injector](https://github.com/ets-labs/python-dependency-injector),
which will allow you to easily migrate to injection
(see [migration from dependency injector](https://injection.readthedocs.io/latest/dev/migration-from-dependency-injector.html));
