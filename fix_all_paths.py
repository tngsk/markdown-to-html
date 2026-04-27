import os
import glob

for f in glob.glob("tests/components/*.py"):
    with open(f, 'r') as file:
        content = file.read()

    if "import sys" not in content:
        content = "import sys\nimport os\nsys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))\n" + content

    with open(f, 'w') as file:
        file.write(content)
