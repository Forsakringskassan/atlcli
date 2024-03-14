#!/usr/bin/sh
# set -x
echo "Testing atlcli bitb get-file-content lines"
./testserver.py files &
atlcli bitb get-file-content -l inputs/get-file-lines.input -u 127.0.0.1 -p 8000 lines '.*version.*' > actual/get-file-lines.output
if [ $? -ne 0 ]
then
  echo "Testing atlcli bitb get-file-content lines"
  curl 127.0.0.1:8000/stop
  exit 1
fi
curl 127.0.0.1:8000/stop
diff -Zb expected/get-projects.output actual/get-projects.output
result=$?
test $result -eq 0 || echo "Failed test atlcli bitb get-file-content lines"
exit $result