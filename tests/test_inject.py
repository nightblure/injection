from injection import Provide, inject
from tests.container_objects import Service


def test_injection_with_args_overriding(container) -> None:
    @inject
    def _inner(
        arg1: bool,  # noqa: FBT001
        arg2: Service = Provide[container.service],
        arg3: int = 100,
    ) -> None:
        _ = arg1
        _ = arg3
        original_obj = container.service()
        assert arg2.a != original_obj.a
        assert arg2.b != original_obj.b

    _inner(True, container.service(b="url", a=2000))  # noqa: FBT003
    _inner(arg1=True, arg2=container.service(b="urljyfuf", a=8400))
    _inner(True, arg2=container.service(b="afdsfsf", a=2242))  # noqa: FBT003


async def test_injection_with_args_overriding_async(container) -> None:
    @inject
    async def _inner(
        arg1: bool,  # noqa: FBT001
        arg2: Service = Provide[container.service],
        arg3: int = 100,
    ) -> None:
        _ = arg1
        _ = arg3
        original_obj = container.service()
        assert arg2.a != original_obj.a
        assert arg2.b != original_obj.b

    await _inner(True, container.service(b="url", a=2000))  # noqa: FBT003
    await _inner(arg1=True, arg2=container.service(b="url", a=2000))
    await _inner(True, arg2=container.service(b="url", a=2000))  # noqa: FBT003


async def test_injection_async(container) -> None:
    @inject
    async def _inner(
        arg1: bool,  # noqa: FBT001
        arg2: Service = Provide[container.service],
        arg3: int = 100,
    ) -> None:
        assert arg1
        assert isinstance(arg2, Service)
        assert arg3 == 100

    await _inner(True)  # noqa: FBT003
