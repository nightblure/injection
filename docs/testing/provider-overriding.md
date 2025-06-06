# Provider overriding

DI container provides, in addition to direct dependency injection, another very important functionality:
**dependencies or providers overriding**.

Any provider registered with the container can be overridden.
This can help you replace objects with simple stubs, or with other objects.
**Override affects all providers that use the overridden provider (_see example_)**.

## Example

```python
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, Engine, text
from testcontainers.postgres import PostgresContainer
from injection import DeclarativeContainer, providers, Provide, inject


class SomeSQLADao:
    def __init__(self, *, sqla_engine: Engine):
        self.engine = sqla_engine
        self._connection = None

    def __enter__(self):
        self._connection = self.engine.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.close()

    def exec_query(self, query: str):
        return self._connection.execute(text(query))


class Settings(BaseSettings):
    db_url: str = 'some_production_db_url'


class DIContainer(DeclarativeContainer):
    settings = providers.Singleton(Settings)
    sqla_engine = providers.Singleton(create_engine, settings.provided.db_url)
    some_sqla_dao = providers.Transient(SomeSQLADao, sqla_engine=sqla_engine)


@inject
def exec_query_example(some_sqla_dao=Provide[DIContainer.some_sqla_dao]):
    with some_sqla_dao:
        result = some_sqla_dao.exec_query('SELECT 234')

    return next(result)


def main():
    pg_container = PostgresContainer(image='postgres:alpine3.19')
    pg_container.start()
    db_url = pg_container.get_connection_url()

    """
    We override only settings, but this override will also affect the 'sqla_engine'
    and 'some_sqla_dao' providers because the 'settings' provider is used by them!
    """
    local_testing_settings = Settings(db_url=db_url)
    DIContainer.settings.override(local_testing_settings)

    try:
        result = exec_query_example()
        assert result == (234,)
    finally:
        DIContainer.settings.reset_override()
        pg_container.stop()


if __name__ == '__main__':
    main()

```

The example above shows how overriding a nested provider ('_settings_')
affects another provider ('_engine_' and '_some_sqla_dao_').

## Override multiple providers

The example above looked at overriding only one settings provider,
but the container also provides the ability to override
multiple providers at once with method ```override_providers```.

The code above could remain the same except that
the single provider override could be replaced with the following code:

```python
def main():
    pg_container = PostgresContainer(image='postgres:alpine3.19')
    pg_container.start()
    db_url = pg_container.get_connection_url()

    local_testing_settings = Settings(db_url=db_url)
    providers_for_overriding = {
        'settings': local_testing_settings,
        # more values...
    }
    with DIContainer.override_providers(providers_for_overriding):
        try:
            result = exec_query_example()
            assert result == (234,)
        finally:
            pg_container.stop()
```

## Overriding of singleton provider
If singleton attribute is used in other singleton or resource and this other provider is initialized,
then in case of overriding of the first singleton, second one will be cached with original value.

Same with resetting overriding. Here is an example.

```python
from dataclasses import dataclass

from injection import Provide, DeclarativeContainer, providers, inject

DEFAULT_REDIS_URL = 'url_1'
MOCK_REDIS_URL = 'url_2'


@dataclass
class Settings:
    redis_url: str = DEFAULT_REDIS_URL


class Redis:
    def __init__(self, url: str) -> None:
        self.url = url


class DIContainer(DeclarativeContainer):
    settings = providers.Singleton(Settings)
    redis = providers.Singleton(Redis, url=settings.provided.redis_url)


@inject
def func(redis: Redis = Provide[DIContainer.redis]):
    return redis.url


def test_case_1() -> None:
    DIContainer.settings.override(Settings(redis_url=MOCK_REDIS_URL))

    assert func() == MOCK_REDIS_URL

    DIContainer.settings.reset_override()
    # DIContainer.redis.reset() # OK

    assert func() == DEFAULT_REDIS_URL  # ASSERTION ERROR


def test_case_2() -> None:
    assert DIContainer.redis().url == DEFAULT_REDIS_URL

    DIContainer.settings.override(Settings(redis_url=MOCK_REDIS_URL))
    # DIContainer.redis.reset() # OK
    
    # Or you can fix like this
    # with DIContainer.override_providers_kwargs(settings=Settings(redis_url=MOCK_REDIS_URL), reset_singletons=True):
        # assert func() == MOCK_REDIS_URL  # OK
    
    assert func() == MOCK_REDIS_URL  # ASSERTION ERROR
    

if __name__ == "__main__":
    test_case_1()
    test_case_2()
```
