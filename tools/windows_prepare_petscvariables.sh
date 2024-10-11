# script for replacing cygwin system paths (/home and /cygdrive/c) with the
# corresponding Windows path (i.e., C:/...)

# ARGS

# \ must be protected!
PETSC_DIR=$1
PETSC_ARCH=$2

PETSC_DIR=$(cygpath -u ${PETSC_DIR})

FILENAME=$PETSC_DIR/$PETSC_ARCH/lib/petsc/conf/petscvariables

PLATFORM=$(uname -o)
if [ $PLATFORM != "Cygwin" ]; then
    echo Platform is not cygwin but ${PLATFORM}
    exit 1
fi

echo "PETSC_DIR     ${PETSC_DIR}"
echo "PETSC_ARCH    ${PETSC_ARCH}"
echo
echo "Patching ${FILENAME}"
echo
# sed pattern to escape slashes, i.e., / to \/
SLASH_ESC='s/[\/]/\\\//g'

HOME_ESC=$(echo $HOME | sed -e $SLASH_ESC)

HOME_WIN=$(cygpath -m $(realpath $HOME))
HOME_WIN_ESC=$(echo $HOME_WIN | sed -e $SLASH_ESC)

CYGWIN_ROOT="/cygdrive/c/"
CYGWIN_ROOT_ESC=$(echo $CYGWIN_ROOT | sed -e $SLASH_ESC)

CYGWIN_ROOT_WIN=$(cygpath -m $CYGWIN_ROOT)
CYGWIN_ROOT_WIN_ESC=$(echo $CYGWIN_ROOT_WIN | sed -e $SLASH_ESC)

# convert /cygdrive/c to C:
echo "Replacing ${CYGWIN_ROOT} with ${CYGWIN_ROOT_WIN}"
sed -i "s/${CYGWIN_ROOT_ESC}/${CYGWIN_ROOT_WIN_ESC}/g" $FILENAME

# convert "/home/user" to "/path/to/cygwin/home/user"
# ignore the line defining "wPETSC_DIR" as this is window already!
echo "Replacing ${HOME} with ${HOME_WIN}"
sed -i "/^wPETSC_DIR/! s/${HOME_ESC}/${HOME_WIN_ESC}/g" $FILENAME

echo "Replacing -lpetsc with -llibpetsc"
sed -i "s/-lpetsc/-llibpetsc/g" $FILENAME
