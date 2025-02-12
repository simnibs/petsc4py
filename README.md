# petsc4py with Precompiled PETSc Libraries

This repository provides [petsc4py](https://petsc.org/main/petsc4py/reference/petsc4py.html) wheels with precompiled libraries. Wheels are available for Windows, Linux, and (ARM64) MacOS.

Below is an overview over what components PETSc is built with on different platforms.


|               | Linux      | MacOS     | Windows   |
|:--------------|:----------:|:---------:|:---------:|
| Architecture  | x64        | arm64     | x64       |
| BLAS/LAPACK   | MKL        | Apple Accelerate | MKL |
| MPI           | MPICH      | MPICH     | MS-MPI    |
| HYPRE         | x          | x         | x         |
| MKL PARDISO   | x          |           | x         |
| MUMPS         |            | x         |           |

Versions and tags of this repository follow the PETSc version on which petsc4py is based.

## TODOs

- General clean-up of workflows. Some things are hardcoded.
- Compile HYPRE against MKL BLAS on linux, windows?

### Windows
- Convert from command prompt to powershell?
- The test with real data using MKL PARDISO with cholesky factorization fails. Not sure why.

### MacOS
- Test threading
- Solve phase of MUMPS is slower than python-mumps. Why?
- MUMPS seems to be statically compiled even with shared-library=1?
- Currently, I set `MACOSX_DEPLOYMENT_TARGET` to 14.0 manually since `cibuildwheel` defaults to 11. I don't know if using 11 would case problems. The current M1 mac runners on GitHub Actions uses MacOS 14.
