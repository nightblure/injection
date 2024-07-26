from typing import ClassVar, List, Type, Union

from injection.base_container import DeclarativeContainer

ContainersType = List[Union[DeclarativeContainer, Type[DeclarativeContainer]]]


class ContainerRegistry:
    __containers: ClassVar[ContainersType] = []

    @classmethod
    def __get_containers(cls) -> ContainersType:
        if not cls.__containers:
            cls.__containers = DeclarativeContainer.__subclasses__()
        return cls.__containers

    @classmethod
    def get_containers_count(cls) -> int:
        return len(cls.__get_containers())

    @classmethod
    def get_default_container(cls) -> Type[DeclarativeContainer]:
        containers = cls.__get_containers()
        if len(containers) == 0:
            msg = "You should create at least one container"
            raise Exception(msg)

        return containers[0]
