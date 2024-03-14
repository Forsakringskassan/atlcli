#!/usr/bin/bash
# Runs the postgresql module installed in virtual environment with hundbidrag database.
set -e
source ../environment.sh || true
[ -d testbox ] || $PYTHON -m venv testbox
[ $MACHINE == "MinGw" ] && ACTIVATE="testbox/Scripts/activate"
[ $MACHINE == "Linux" ] && ACTIVATE="testbox/bin/activate"
source $ACTIVATE
$PYTHON -m postgresqlpatches ../examples/hundbidrag/*.sql
