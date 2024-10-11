# execute
#
# call "%ProgramFiles(x86)%\Intel\oneAPI\setvars"
#
# before calling this script. This sets intel and msvc variables, paths, etc.
#
# sets MKLROOT etc.
# adds ifort to path

PLATFORM=$(uname -o)
if [ $PLATFORM != "Cygwin" ]; then
    echo Platform is not cygwin but ${PLATFORM}
    exit 1
fi

PETSC_VERSION=$1            # e.g., 3.21.4
export PETSC_ARCH=$2        # arch-mswin-c-opt-mkl

# MKL
if [ -z "${MKLROOT}" ]; then
    echo MKLROOT not set.
    exit 1
else
     MKLROOT=$(cygpath -u $(cygpath -ms "${MKLROOT}"))
     MKL_INC=$MKLROOT/include
     MKL_LIB=$MKLROOT/lib
fi

# HYPRE
if [ -z "${HYPRE_INSTALL_DIR}" ]; then
    echo HYPRE_INSTALL_DIR not set
    exit 1
else
    HYPRE_INSTALL_DIR=$(cygpath -u $(cygpath -ms "${HYPRE_INSTALL_DIR}"))
    HYPRE_BIN=$HYPRE_INSTALL_DIR/bin
    HYPRE_INC=$HYPRE_INSTALL_DIR/include
    HYPRE_LIB=$HYPRE_INSTALL_DIR/lib
fi

# # MSMPI
if [ -z "${MSMPI_BIN}" ]; then
    echo MSMPI_BIN not set
    exit 1
else
    MSMPI_BIN=$(cygpath -u $(cygpath -ms "${MSMPI_BIN}"))
fi

if [ -z "${MSMPI_INC}" ]; then
    echo MSMPI_INC not set
    exit 1
else
    MSMPI_INC=$(cygpath -u $(cygpath -ms "${MSMPI_INC}"))

fi

if [ -z "${MSMPI_LIB64}" ]; then
    echo MSMPI_LIB64 not set
    exit 1
else
    MSMPI_LIB64=$(cygpath -u $(cygpath -ms "${MSMPI_LIB64}"))
fi

PETSC_NAME=petsc-${PETSC_VERSION}
if [ ! -d "${PETSC_VERSION}" ]; then
    echo "Downloading PETSc ${PETSC_VERSION}"
    curl -O -L https://web.cels.anl.gov/projects/petsc/download/release-snapshots/${PETSC_NAME}.tar.gz
    tar -xzf ${PETSC_NAME}.tar.gz
fi

# NOTE
# Currently (08/2024), ifx (the successor to ifort) only works with
# --with-shared-library=0. Consequently, we use ifort despite it being
# deprecated.
if ! command -v ifort &> /dev/null; then
    echo "ifort could not be found"
    exit 1
fi

export PETSC_DIR=$(realpath $PWD/$PETSC_NAME)
cd $PETSC_DIR

echo ==========================================================================
echo PETSc
echo "   PETSC_DIR  $PETSC_DIR"
echo "   PETSC_ARCH $PETSC_ARCH"
echo
echo "HYPRE"
echo "   BIN        $HYPRE_BIN"
echo "   INCLUDE    $HYPRE_INC"
echo "   LIB        $HYPRE_LIB"
echo "MSMPI"
echo "   BIN        $MSMPI_BIN"
echo "   INCLUDE    $MSMPI_INC"
echo "   LIB        $MSMPI_LIB64"
echo "Intel OneAPI"
echo "   INCLUDE    $MKL_INC"
echo "   LIB        $MKL_LIB"

echo ==========================================================================

if [ -f "/usr/bin/link.exe" ]; then
    echo "Renaming cygwin's link.exe to link-cygwin.exe"
    mv /usr/bin/link.exe /usr/bin/link-cygwin.exe
fi

# fp:precise

# We need to point to Cygwin's make on Github Actions windows runners as
# otherwise gmake from a perl distribution seems to be used!

./configure \
    --with-cc='win32fe cl' \
    --with-cxx='win32fe cl' \
    --with-fc='win32fe ifort' \
    --with-fortran-bindings=0 \
    --with-debugging=0 \
    --COPTFLAGS='-O2' \
    --CXXOPTFLAGS='-O2' \
    --FOPTFLAGS='-O2' \
    --with-mpi-include=\[$MSMPI_INC,$MSMPI_INC/x64\] \
    --with-mpi-lib=\[$MSMPI_LIB64/msmpi.lib,$MSMPI_LIB64/msmpifec.lib\] \
    --with-mpiexec=$MSMPI_BIN/mpiexec \
    --with-hypre-include=$HYPRE_INC \
    --with-hypre-lib=$HYPRE_LIB/HYPRE.lib \
    --with-blaslapack-lib=\[$MKL_LIB/mkl_core_dll.lib,$MKL_LIB/mkl_intel_lp64_dll.lib,$MKL_LIB/mkl_intel_thread_dll.lib\] \
    --with-mkl_pardiso-include=$MKL_INC \
    --with-mkl_pardiso-lib=\[$MKL_LIB/mkl_core_dll.lib,$MKL_LIB/mkl_intel_lp64_dll.lib,$MKL_LIB/mkl_intel_thread_dll.lib\] \
    --with-make-exec=/usr/bin/make \
    --with-shared-libraries=1

make all
# We need to add the path to the HYPRE dll in order for the checks to succeed
# (ldd $PETSC_DIR/$PETSC_ARCH/lib/libpetsc.dll will show that HYPRE.dll is not
# found).
echo Adding HYPRE to PATH : ${HYPRE_BIN}
export PATH=$PATH:${HYPRE_BIN}
make check
