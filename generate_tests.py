import os
from pathlib import Path
import re

components_dir = Path("src/components")
tests_dir = Path("tests/components")
tests_dir.mkdir(exist_ok=True)

# Find all components with parser.py
components_with_parsers = []
for p in components_dir.iterdir():
    if p.is_dir() and (p / "parser.py").exists():
        components_with_parsers.append(p.name)

# Find existing tests
existing_tests = []
for p in tests_dir.glob("test_mono_*.py"):
    existing_tests.append(p.stem.replace("test_", "").replace("_", "-"))

for comp in components_with_parsers:
    comp_underscored = comp.replace('-', '_')
    test_file = tests_dir / f"test_{comp_underscored}.py"
    if not test_file.exists():
        print(f"Need to create test for {comp}")
