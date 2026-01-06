from typing import Dict, List, Tuple, Type, Union


class ParserRegistry:
    _registry: Dict[str, Type] = {}

    @classmethod
    def register(cls, extensions: Union[str, List[str], Tuple[str, ...]]):
        def decorator(parser_class):
            if isinstance(extensions, (list, tuple)):
                for ext in extensions:
                    cls._registry[ext.lower()] = parser_class
            else:
                cls._registry[extensions.lower()] = parser_class
            return parser_class

        return decorator

    @classmethod
    def get_parser(cls, extension: str):
        parser_class = cls._registry.get(extension.lower())
        if not parser_class:
            raise ValueError(f"No parser registered for extension '{extension}'")
        return parser_class()