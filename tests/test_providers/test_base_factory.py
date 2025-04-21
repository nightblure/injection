from injection.providers import Coroutine, Factory, Object


def test_has_async_dependencies_expect_false_without_dependencies() -> None:
    provider = Factory(lambda: None)

    assert provider.has_async_dependencies() is False


def test_has_async_dependencies_expect_false_without_base_factory_dependencies() -> (
    None
):
    def _factory(arg: int) -> int:
        return arg + 1

    provider = Factory(_factory, arg=3)

    assert provider.has_async_dependencies() is False


def test_has_async_dependencies_expect_false_with_other_type_dependencies() -> None:
    class SomeClass:
        def __init__(self, dependency: int) -> None:
            self.dependency = dependency

    provider = Factory(SomeClass, Object(5).cast)

    assert provider.has_async_dependencies() is False


def test_has_async_dependencies_expect_true_with_only_one_async_dependency() -> None:
    async def _async_factory() -> int:
        return 5

    class SomeClass:
        def __init__(self, dependency: int) -> None:
            self.dependency = dependency

    provider = Factory(SomeClass, Coroutine(_async_factory).cast)

    assert provider.has_async_dependencies()


def test_has_async_dependencies_expect_true_with_async_and_sync_dependencies() -> None:
    async def _async_factory() -> int:
        return 5

    def _sync_factory() -> str:
        return "string"

    class SomeClass:
        def __init__(self, dependency: int, another_dependency: str) -> None:
            self.dependency = dependency
            self.another_dependency = another_dependency

    provider = Factory(
        SomeClass,
        dependency=Coroutine(_async_factory).cast,
        another_dependency=Factory(_sync_factory).cast,
    )

    assert provider.has_async_dependencies()
