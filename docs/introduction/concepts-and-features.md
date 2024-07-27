# Concepts and features

## Concept
With `Injection` you can implement the principle of **Dependency Injection**.
**Dependency Injection** (**DI**) - providing a process to an external software component.
This is a specific form of “**inversion of control**” (**IoC**) when applied to dependency management.
In accordance with the verification principle, the responsible entity outsources the construction
of the dependencies it requires from outside, specifically designed for this general mechanism
([Wikipedia source](https://en.wikipedia.org/wiki/Dependency_injection)).

Using this framework you can reduce [coupling](https://en.wikipedia.org/wiki/Coupling_(computer_programming))
and stop monkeypatching your tests.
Instead of monkeypatching you can pass mock objects or any other objects as parameters.

---

## Features

The public API of this framework is almost completely identical to
[Dependency Injector](https://python-dependency-injector.ets-labs.org/index.html#),
because the author found it successful and understandable.
In addition, this will provide an easy migration to the current framework with
[Dependency Injector](https://python-dependency-injector.ets-labs.org/index.html#)
(see [migration from Dependency Injector](https://injection.readthedocs.io/latest/dev/migration-from-dependency-injector.html)).
Other features and advantages:

* support **Python 3.8-3.12**;
* works with **FastAPI, Flask, Litestar** and **Django REST Framework**;
* dependency injection via `Annotated` in FastAPI;
* **no third-party dependencies**;
* **multiple containers**;
* providers - delegate object creation and lifecycle management to providers;
* **overriding** dependencies for tests without wiring;
* **100%** code coverage and very simple code.
