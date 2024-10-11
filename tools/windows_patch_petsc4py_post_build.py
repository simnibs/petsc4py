from pathlib import Path
import sys

petsc4py_dir = Path(sys.argv[1])

filename = petsc4py_dir / "petsc4py" / "lib" / "__init__.py"

patch = """

# start patch

# this is similar in spirit to what delvewheel does
depth = 4
dll_dir = r"Library\\bin"

import os
libs_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        os.pardir,
        os.pardir,
        os.pardir,
        dll_dir,
    )
)
if os.path.isdir(libs_dir):
    os.add_dll_directory(libs_dir)

# end patch

"""

with open(filename, "r") as f:
    content = f.read()

content += patch

with open(filename, "w") as f:
    f.write(content)
