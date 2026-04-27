import os
from pathlib import Path
import importlib.util

components_dir = Path("src/components")

def load_parser(comp_name):
    parser_path = components_dir / comp_name / "parser.py"
    if not parser_path.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"{comp_name}_parser", parser_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Parser()

for p in components_dir.iterdir():
    if p.is_dir() and (p / "parser.py").exists():
        parser = load_parser(p.name)
        print(f"{p.name}: pattern = {getattr(parser, 'PATTERN', None)}")
