# Migration from Dependency Injector

If you have already used a wonderful package
[dependency-injector](https://github.com/ets-labs/python-dependency-injector),
then you probably know that there have been no new versions for a long time.
It also lacks integration with FastAPI, for example to determine dependencies with **Annotated**
(see [issues](https://github.com/ets-labs/python-dependency-injector/issues?q=is%3Aissue+is%3Aopen+annotated)).
[Injection](https://github.com/nightblure/injection) package has an almost identical API to the [dependency-injector](https://github.com/ets-labs/python-dependency-injector)
and eliminates its shortcomings, which will make migrating very easy.

---

⚠️ **IMPORTANT** ❗

[Injection](https://github.com/nightblure/injection) **does not implement** **some** [providers](https://python-dependency-injector.ets-labs.org/providers/index.html)
(Resource, List, Dict, Aggregate and etc.) because the developer considered them to be **rarely used** in practice.
In this case, you don't need to do the migration, but if you really want to use my package,
I'd love to see your [issues](https://github.com/nightblure/injection/issues) and/or [MR](https://github.com/nightblure/injection/pulls)!

---

To **migrate**, follow these **steps**:
1. **Replace imports**:
* `from dependency_injector import providers` -> `from injection import providers`;

* `from dependency_injector.wiring import Provide, inject` -> `from injection import Provide, inject`

* `from dependency_injector.containers import DeclarativeContainer` -> `from injection import DeclarativeContainer`

2. **Replace method call**: `some_container.override_providers(**overrides)` -> ``some_container.override_providers(overrides)``
