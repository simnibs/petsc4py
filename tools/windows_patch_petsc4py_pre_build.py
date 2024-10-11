"""

Patch setup.cfg to find msmpi library.

"""
from pathlib import Path
import sys

petsc4py_dir = Path(sys.argv[1])

setupcfg = petsc4py_dir / "setup.cfg"

patch = """

# start patch

[build_ext]
libraries = msmpi
library_dirs = C:/Program Files (x86)/Microsoft SDKs/MPI/Lib/x64

# end patch

"""

with open(setupcfg, "r") as f:
    content = f.read()

assert "[build_ext]" not in content, (
    "`build_ext` section already defined in setup.cfg. ",
    "Please check the validity of this patch."
)

content += patch

with open(setupcfg, "w") as f:
    f.write(content)
