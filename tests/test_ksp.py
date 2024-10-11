import sys
import time

import numpy as np
import pytest
import scipy as sp

from petsc4py import PETSc

"""Based on example from https://tbetcke.github.io/hpc_lecture_notes/petsc_for_sparse_systems.html"""

@pytest.fixture
def stiffness_matrix():
    S = sp.sparse.load_npz("data/system_matrix.npz")
    A = PETSc.Mat(comm=PETSc.COMM_WORLD)
    A.createAIJ(size=S.shape, csr=(S.indptr, S.indices, S.data))
    A.assemble()
    return A

@pytest.fixture
def rhs_vectors():
    return np.load("data/system_rhs.npz")["arr_0"]

@pytest.fixture
def sol_vectors():
    return np.load("data/system_sol.npz")["arr_0"]

def build_A(n=1000):
    """Create empty matrix and fill."""

    nnz = 3 * np.ones(n, dtype=np.int32)
    nnz[0] = nnz[-1] = 2

    A = PETSc.Mat()
    A.createAIJ([n, n], nnz=nnz)

    # First set the first row
    A.setValue(0, 0, 2)
    A.setValue(0, 1, -1)
    # Now we fill the last row
    A.setValue(n-1, n-2, -1)
    A.setValue(n-1, n-1, 2)

    # And now everything else
    for index in range(1, n - 1):
        A.setValue(index, index - 1, -1)
        A.setValue(index, index, 2)
        A.setValue(index, index + 1, -1)

    A.assemble()

    return A

def build_A_from_csr_array(n=1000):
    """Create empty matrix and fill from scipy sparse csr array."""

    # First set the first row
    row_ind = [0, 0, n-1, n-1]
    col_ind = [0, 1, n-2, n-1]
    data = [2, -1, -1, 2]

    # And now everything else
    for index in range(1, n - 1):
        row_ind.append(index)
        col_ind.append(index-1)
        data.append(-1)

        row_ind.append(index)
        col_ind.append(index)
        data.append(2)

        row_ind.append(index)
        col_ind.append(index+1)
        data.append(-1)

    data = np.array(data, dtype=np.int32)
    row_ind = np.array(row_ind, dtype=np.int32)
    col_ind = np.array(col_ind, dtype=np.int32)

    ss_arr = sp.sparse.csr_array((data, (row_ind, col_ind)))

    A = PETSc.Mat()
    A.createAIJ(size=ss_arr.shape, csr=(ss_arr.indptr, ss_arr.indices, ss_arr.data))
    A.assemble()

    return A

class TestMat:

    @pytest.mark.parametrize("n", [100, 1000])
    def test_mat_build_methods(self, n):
        A0 = build_A(n)
        A1 = build_A_from_csr_array(n)
        assert A0.equal(A1)
        # np.testing.assert_allclose()


    @pytest.mark.parametrize("n", [100, 1000])
    def test_mat(self, n):
        A = build_A(n)
        assert A.size == (n, n)

        diagonals = A.getDiagonal().array
        assert np.all(diagonals == 2)

class TestKSP:
    @pytest.mark.parametrize(
        ["ksp_type", "pc_type","factor_solver_type"],
        [
            ("cg", "none", None),
            ("cg", "hypre", None),
            pytest.param(
                "preonly",
                "lu",
                "mkl_pardiso",
                marks=pytest.mark.skipif(
                    sys.platform == "darwin",
                    reason="PETSc is not built with Intel MKL on macos."
                ),
            ),
            pytest.param(
                "preonly",
                "cholesky",
                "mkl_pardiso",
                marks=pytest.mark.skipif(
                    sys.platform == "darwin",
                    reason="PETSc is not built with Intel MKL on macos."
                ),
            ),
            pytest.param(
                "preonly",
                "lu",
                "mumps",
                marks=pytest.mark.skipif(
                    sys.platform != "darwin",
                    reason="PETSc only built with MUMPS on macos."
                ),
            ),
            pytest.param(
                "preonly",
                "cholesky",
                "mumps",
                marks=pytest.mark.skipif(
                    sys.platform != "darwin",
                    reason="PETSc only built with MUMPS on macos."
                ),
            ),
        ]
    )
    def test_KSP(self, ksp_type, pc_type, factor_solver_type, rtol=1e-10):

        A = build_A()

        b = A.createVecLeft()
        b.array[:] = 1

        x = A.createVecRight()

        # Build KSP solver object
        ksp = PETSc.KSP().create()
        ksp.setOperators(A)
        ksp.setTolerances(rtol=rtol)
        ksp.setType(ksp_type)
        ksp.setConvergenceHistory()
        ksp.getPC().setType(pc_type)
        if factor_solver_type is not None:
            ksp.getPC().setFactorSolverType(factor_solver_type)

        # solve
        ksp(b, x)

        b_hat = A.createVecLeft()
        A.mult(x, b_hat)

        # print(ksp.getConvergenceHistory()[-1])

        # ksp.KSP_CONVERGED_RTOL # 2
        # assert ksp.getConvergedReason() == ksp.KSP_CONVERGED_RTOL

        #assert np.isclose(0, ksp.getConvergenceHistory()[-1])
        np.testing.assert_allclose(b[:], b_hat[:])

    @pytest.mark.parametrize(
        ["ksp_type", "pc_type","factor_solver_type"],
        [
            #(PETSc.KSP.Type.CG, "none", None),
            (PETSc.KSP.Type.CG, PETSc.PC.Type.HYPRE, None),
            pytest.param(
                PETSc.KSP.Type.PREONLY,
                PETSc.PC.Type.LU,
                PETSc.Mat.SolverType.MKL_PARDISO,
                marks=pytest.mark.skipif(
                    sys.platform == "darwin",
                    reason="PETSc is not built with Intel MKL on macos."
                ),
            ),
            pytest.param(
                PETSc.KSP.Type.PREONLY,
                PETSc.PC.Type.CHOLESKY,
                PETSc.Mat.SolverType.MKL_PARDISO,
                marks=[
                    pytest.mark.skipif(
                    sys.platform == "darwin",
                    reason="PETSc is not built with Intel MKL on macos."
                    ),
                    pytest.mark.xfail(
                        sys.platform == "win32",
                        reason="This fails on GitHub Actions windows-2022 but not locally.",
                    ),
                ],
            ),
            pytest.param(
                PETSc.KSP.Type.PREONLY,
                PETSc.PC.Type.LU,
                PETSc.Mat.SolverType.MUMPS,
                marks=pytest.mark.skipif(
                    sys.platform != "darwin",
                    reason="PETSc only built with MUMPS on macos."
                ),
            ),
            pytest.param(
                PETSc.KSP.Type.PREONLY,
                PETSc.PC.Type.CHOLESKY,
                PETSc.Mat.SolverType.MUMPS,
                marks=pytest.mark.skipif(
                    sys.platform != "darwin",
                    reason="PETSc only built with MUMPS on macos."
                ),
            ),
        ]
    )
    def test_KSP_real(
        self,
        stiffness_matrix,
        rhs_vectors,
        sol_vectors,
        ksp_type,
        pc_type,
        factor_solver_type,
        rtol=1e-10,
        ):
        # ksp_type PREONLY uses only a single application of the preconditioner

        A = stiffness_matrix

        # Build KSP solver object
        ksp = PETSc.KSP()
        ksp.create(comm=A.getComm())
        ksp.setOperators(A)
        ksp.setTolerances(rtol=rtol)
        ksp.setType(ksp_type)
        ksp.setConvergenceHistory()

        # setup PC
        ksp.getPC().setType(pc_type)
        if ksp.getPC().getType() == "hypre":
            ksp.getPC().setHYPREType("boomeramg")

            # This option cannot be set from the python interface directly
            #-pc_hypre_boomeramg_coarsen_type HMIS
            options = PETSc.Options()
            options["pc_hypre_boomeramg_coarsen_type"] = "HMIS"
            ksp.getPC().setFromOptions()

        # setup factor solver
        if factor_solver_type is not None:
            ksp.getPC().setFactorSolverType(factor_solver_type)
            # MUMPS: to explicitly set the permutation analysis tool to METIS
            # ksp.getPC().getFactorMatrix().setMumpsIcntl(7, 5)

        init_time = time.perf_counter()

        print("Preparing KSP")
        # PC preparation
        start = time.perf_counter()
        ksp.setUp()
        print(f"Time to prepare KSP: {time.perf_counter() - start:.4f} s")

        b = A.createVecLeft()
        x = A.createVecRight()

        for thisrhs,s in zip(rhs_vectors, sol_vectors):

            b.array[:] = thisrhs

            # solve
            start = time.perf_counter()
            ksp.solve(b, x)
            print(f"Time to solve: {time.perf_counter()-start:.4f} s")

            # print(ksp.getResidualNorm())
            assert np.allclose(x[:], s)

        print(f"Total time: {time.perf_counter()-init_time:.4f} s")
