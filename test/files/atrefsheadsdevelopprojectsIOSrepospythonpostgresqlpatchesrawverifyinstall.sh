#!/usr/bin/bash
# Installs the postgresql wheel in local virtual environment. Parameter should be the wheel relative to
# parent directory (it is intended to be called from autobuild). Like this:
# ./install.sh ../dist/postgresqlpatches-0.2.0+20230503075657-py3-none-any.whl
set -e
source ../environment.sh || true
[ -d testbox ] || $PYTHON -m venv testbox
[ $MACHINE == "MinGw" ] && ACTIVATE="testbox/Scripts/activate"
[ $MACHINE == "Linux" ] && ACTIVATE="testbox/bin/activate"
source $ACTIVATE
$PYTHON -m pip install $1
$PYTHON -m pip install pip-system-certs==4.0
$PYTHON -m pip install jake==3.0.0
