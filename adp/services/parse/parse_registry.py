from typing import Dict, List, Tuple, Type, Union


class ParseRegistry:
    _registry: Dict[str, Type] = {}

    @classmethod
    def register(cls, extensions: Union[str, List[str], Tuple[str, ...]]):
        def decorator(parse_class):
            if isinstance(extensions, (list, tuple)):
                for ext in extensions:
                    cls._registry[ext.lower()] = parse_class
            else:
                cls._registry[extensions.lower()] = parse_class
            return parse_class

        return decorator

    @classmethod
    def get_parse(cls, extension: str):
        parse_class = cls._registry.get(extension.lower())
        if not parse_class:
            raise ValueError(f"No parse registered for extension '{extension}'")
        return parse_class()
