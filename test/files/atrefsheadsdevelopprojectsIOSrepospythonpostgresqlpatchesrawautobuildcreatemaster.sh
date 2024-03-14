#!/usr/bin/bash
MASTER_ROOT=$SETUP_DIR_NAME/autobuild/master_root
[ -d $MASTER_ROOT ] || mkdir $MASTER_ROOT
pushd $MASTER_ROOT
echo $PYTHON
[ -d sandbox ] || $PYTHON -m venv sandbox
[ $MACHINE == "MinGw" ] && ACTIVATE="sandbox/Scripts/activate"
[ $MACHINE == "Linux" ] && ACTIVATE="sandbox/bin/activate"
source $ACTIVATE
$PYTHON -m pip install --upgrade pip
$PYTHON -m pip install build==0.10.0
$PYTHON -m pip install buildbot[bundle]==3.8.0
$PYTHON -m pip install requests[security]==2.28.2
# $PYTHON -m pip install twine==4.0.2 # Conflicting dependency to rich also needed by jake
$PYTHON -m pip install twine==3.7.1
$PYTHON -m pip install virtualenv==20.21.0
$PYTHON -m pip install keyring==23.13.1
$PYTHON -m pip install psycopg2==2.9.5
$PYTHON -m pip install setuptools==67.6.1
$PYTHON -m pip install pip-system-certs==4.0
$PYTHON -m pip install wheel==0.40.0
$PYTHON -m pip install spdb-tools==0.2.3
$PYTHON -m pip install atlcli==1.0.0
$PYTHON -m pip install jake==3.0.0

[ $MACHINE == "MinGw" ] && $PYTHON -m pip install pywin32
[ -f my_master/buildbot.tac ] || buildbot create-master my_master
[ -d my_master/gitpoller-workdir ] || mkdir my_master/gitpoller-workdir
[ -f my_master/master.cfg ] || cp my_master/master.cfg.sample my_master/master.cfg
echo ${PYTHON_POSTGRESQL_PATCHES_BRANCHES}
[ -f my_master/twistd.log ] && rm my_master/twistd.log
echo "================== TODO ============================"
echo "Setup environment: 'source ../environment.sh'"
echo "Start sandbox:     'source master_root/$ACTIVATE'"
echo "Start buildbot:    'buildbot --verbose start master_root/my_master'"
echo "See log:           'tail master_root/my_master/twistd.log'"