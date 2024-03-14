SCRIPT_NAME=${BASH_SOURCE[0]}
REAL_PATH=`realpath $SCRIPT_NAME`
export SETUP_DIR_NAME=`dirname $REAL_PATH`
export PYTHONPATH=${PYTHONPATH:+${PYTHONPATH}:}$SETUP_DIR_NAME
echo $SETUP_DIR_NAME
export PYTHONIOENCODING=utf-8
UNAME_OUT="$(uname -s)"
case "${UNAME_OUT}" in
    Linux*)     export MACHINE=Linux;;
    Darwin*)    export MACHINE=Mac;;
    CYGWIN*)    export MACHINE=Cygwin;;
    MINGW*)     export MACHINE=MinGw;;
    *)          export MACHINE="UNKNOWN:${UNAME_OUT}"
esac
echo ${MACHINE}
[ $MACHINE == "MinGw" ] && export PYTHON="python"
[ $MACHINE == "Linux" ] && export PYTHON="python3"
echo $PYTHON
[ $MACHINE == "MinGw" ] && export GIT_BIN=`cygpath -m /mingw64/bin/git`
[ $MACHINE == "Linux" ] && export GIT_BIN=`which git`
echo $GIT_BIN
[ -z "${NEXUS_IQ_USERNAME}" ] && echo "Environment variable NEXUS_IQ_USERNAME not set"
[ -z "${NEXUS_IQ_PASSWORD}" ] && echo "Environment variable NEXUS_IQ_PASSWORD not set"
[ -z "${TWINE_USERNAME}" ] && echo "Environment variable TWINE_USERNAME not set"
[ -z "${TWINE_PASSWORD}" ] && echo "Environment variable TWINE_PASSWORD not set"