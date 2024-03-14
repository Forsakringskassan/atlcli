#!/usr/bin/sh
# set -x
echo "Testing atlcli bitb get-pr-diff"
./testserver.py files &
atlcli bitb get-pr-diff  -l inputs/get-pr-diff.input -u 127.0.0.1 -p 8000 > actual/get-pr-diff.output
if [ $? -ne 0 ]
then
  echo "Failed testing atlcli bitb get-pr-diff"
  curl 127.0.0.1:8000/stop
  exit 1
fi
curl 127.0.0.1:8000/stop
diff -Zb expected/get-pr-diff.output actual/get-pr-diff.output
result=$?
test $result -eq 0 || echo "Failed atlcli bitb get-pr-diff"
exit $result