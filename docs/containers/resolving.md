# Providers and resolving

## Providers

Providers are a wrapper over the objects you plan to use in your application code. Providers are able to work with different objects, but for the same purpose - for resolving and assembling objects. At a minimum, there are the following reasons (and clear advantages) for introducing an abstraction such as a provider:
- ability to distinguish ‘normal’ function parameters from providers in order to automatically **inject** arguments using the ``@inject`` decorator;

- object **lifecycle management**;

- **simple** and ubiquitous **reuse** - instead of another object build with parameter injection,
you just need to ask the provider to resolve the object to be wrapped, the provider will do it all by itself;

- possibility of **overriding/substitution** of object parameters and the object itself for other objects
(which is incredibly useful when writing tests);

- **declarative style of building** complex objects with all the advantages of the above included.


## Resolving

**Resolving** is the **process** of **building and receiving** a ready-to-use object from the provider.
You can ask the provider to build and give you a ready-to-use object,
you just need to tell the provider the rules for building it -
usually a future object class or callable-object and positional and/or keyword arguments.
Please refer to the documentation section with the available providers
([transient](https://injection.readthedocs.io/latest/providers/transient.html),
[singeton](https://injection.readthedocs.io/latest/providers/singleton.html) and etc.)

Below is an **example** of a provider definition and a resolving object representing a container for storing some data:
```python3
from dataclasses import dataclass

from injection.providers.transient import Transient


@dataclass
class SomeDataclass:
    int_value: int
    some_string_value: str


if __name__ == '__main__':
    provider = Transient(SomeDataclass, int_value=5, some_string_value='hello')
    resolved_object = provider()
    print(resolved_object)

    >>  .venv/bin/python3 example.py
        SomeDataclass(int_value=5, some_string_value='hello')

        Process finished with exit code 0
```
