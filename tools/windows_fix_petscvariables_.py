from pathlib import Path
import sys

PETSC_DIR = sys.argv[1]
PETSC_ARCH = sys.argv[2]

filename = Path(PETSC_DIR) / PETSC_ARCH / "lib" / "petsc" / "conf" / "petscvariables"

with open(filename, "r") as f:
    for line in f.readlines():
        if line.startswith("wPETSC_DIR"):
            continue
        elif line.startswith("PETSC_LIB_BASIC"):
            line = line.replace("-llibpetsc", "-lpetsc")
        else:
            line = line.replace("/cygdrive/c/", "C:/")


    content = f.read()

content = content.replace("PETSC_LIB_BASIC = -lpetsc", "PETSC_LIB_BASIC = -llibpetsc")

with open(filename, "w") as f:
    f.write(content)
