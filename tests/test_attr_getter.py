import random
from dataclasses import dataclass, field
from typing import Union

import pytest

from injection.provided import _get_value_from_object_by_dotted_path
from injection.providers.singleton import Singleton


@dataclass
class Nested2:
    some_const = 144


@dataclass
class Nested1:
    nested2_attr: Nested2 = field(default_factory=Nested2)


@dataclass
class Settings:
    some_str_value: str = "some_string_value"
    some_int_value: int = 3453621
    nested1_attr: Nested1 = field(default_factory=Nested1)


@dataclass
class NestingTestDTO: ...


@pytest.fixture
def some_settings_provider() -> Singleton[Settings]:
    return Singleton(Settings)


def test_attr_getter_with_zero_attribute_depth(
    some_settings_provider: Singleton[Settings],
) -> None:
    provided = some_settings_provider.provided.some_str_value

    assert provided.get_value() == Settings().some_str_value


def test_attr_getter_with_more_than_zero_attribute_depth(
    some_settings_provider: Singleton[Settings],
) -> None:
    provided = some_settings_provider.provided.nested1_attr.nested2_attr.some_const

    assert provided.get_value() == Nested2().some_const


@pytest.mark.parametrize(
    ("field_count", "test_field_name", "test_value"),
    [
        (1, "test_field", "sdf6fF^SF(FF*4ffsf"),
        (5, "nested_field", -252625),
        (50, "50_lvl_field", 909234235),
    ],
)
def test_nesting_levels(
    field_count: int,
    test_field_name: str,
    test_value: Union[str, int],
) -> None:
    obj = NestingTestDTO()
    fields = [f"field_{i}" for i in range(1, field_count + 1)]
    random.shuffle(fields)

    attr_path = ".".join(fields) + f".{test_field_name}"
    obj_copy = obj

    while fields:
        field_name = fields.pop(0)
        setattr(obj_copy, field_name, NestingTestDTO())
        obj_copy = obj_copy.__getattribute__(field_name)

    setattr(obj_copy, test_field_name, test_value)

    attr_value = _get_value_from_object_by_dotted_path(obj, attr_path)

    assert attr_value == test_value
