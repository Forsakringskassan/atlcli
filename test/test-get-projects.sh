#!/usr/bin/sh
# set -x
echo "Testing atlcli bitb get-projects"
./testserver.py traces/get-projects.trace &
atlcli bitb get-projects -n IOS -u 127.0.0.1 -p 8000 > actual/get-projects.output
if [ $? -ne 0 ]
then
  echo "Failed testing atlcli bitb get-projects"
  curl 127.0.0.1:8000/stop
  exit 1
fi
atlcli bitb get-projects -n IOS -f KEY -u 127.0.0.1 -p 8000 > actual/get-projects-key.output
if [ $? -ne 0 ]
then
  echo "Failed testing atlcli bitb get-projects -f KEY"
  curl 127.0.0.1:8000/stop
  exit 1
fi
atlcli bitb get-projects -n IOS -f NAME -u 127.0.0.1 -p 8000 > actual/get-projects-name.output
if [ $? -ne 0 ]
then
  echo "Failed testing atlcli bitb get-projects -f NAME"
  curl 127.0.0.1:8000/stop
  exit 1
fi
atlcli bitb get-projects -n IOS -f BOTH -u 127.0.0.1 -p 8000 > actual/get-projects-both.output
if [ $? -ne 0 ]
then
  echo "Failed testing atlcli bitb get-projects -f BOTH"
  curl 127.0.0.1:8000/stop
  exit 1
fi
curl 127.0.0.1:8000/stop
diff -Zb actual/get-projects.output expected/get-projects.output
test $? -eq 0 || { echo "Failed test atlcli bitb get-projects"; exit 1; }
diff -Zb actual/get-projects-key.output expected/get-projects.output
test $? -eq 0 || { echo "Failed test atlcli bitb get-projects -f KEY"; exit 1; }
diff -Zb actual/get-projects-name.output expected/get-projects-name.output
test $? -eq 0 || { echo "Failed test atlcli bitb get-projects -f NAME"; exit 1; }
diff -Zb actual/get-projects-both.output expected/get-projects-both.output
test $? -eq 0 || { echo "Failed test atlcli bitb get-projects -f BOTH"; exit 1; }
exit 0