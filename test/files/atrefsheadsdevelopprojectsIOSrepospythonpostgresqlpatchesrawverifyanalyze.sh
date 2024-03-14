#!/usr/bin/bash
# Analyzes the postgresql module installed in virtual environment usin jake.
set -e
source ../environment.sh || true
[ -d testbox ] || $PYTHON -m venv testbox
[ $MACHINE == "MinGw" ] && ACTIVATE="testbox/Scripts/activate"
[ $MACHINE == "Linux" ] && ACTIVATE="testbox/bin/activate"
source $ACTIVATE
jake iq -s https://secscan.mynd.se:443 -u $NEXUS_IQ_USERNAME -p $NEXUS_IQ_PASSWORD -i postgresqlpatches
