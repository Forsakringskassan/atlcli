#!/usr/bin/bash
# Analyzes the atlcli module installed in virtual environment using jake.
set -e
source ../environment.sh || true
[ -d testbox ] || $PYTHON -m venv testbox
[ $MACHINE == "MinGw" ] && ACTIVATE="testbox/Scripts/activate"
[ $MACHINE == "Linux" ] && ACTIVATE="testbox/bin/activate"
source $ACTIVATE
jake iq -s https://secscan.myndigheten.se:443 -u $NEXUS_IQ_USERNAME -p $NEXUS_IQ_PASSWORD -i IOS_atlcli