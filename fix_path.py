import os
import glob

for f in glob.glob("tests/components/*.py"):
    with open(f, 'r') as file:
        content = file.read()

    content = content.replace("sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))", "sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))")

    with open(f, 'w') as file:
        file.write(content)
