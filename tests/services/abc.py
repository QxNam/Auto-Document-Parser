from adp.services.parse.parse_registry import ParseRegistry
import adp.services.parse # Import package để kích hoạt __init__.py

print(f"Registered extensions: {list(ParseRegistry._registry.keys())}")