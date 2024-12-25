class DuplicatedFactoryTypeAutoInjectionError(Exception):
    def __init__(self, type_: str) -> None:
        message = (
            f"Cannot resolve auto inject because found "
            f"more than one provider for type '{type_}'"
        )
        super().__init__(message)


class UnknownProviderTypeAutoInjectionError(Exception):
    def __init__(self, type_: str) -> None:
        message = f"Provider with type {type_!r} not found"
        super().__init__(message)
