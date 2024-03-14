#!/usr/bin/sh
# TODO
set -x
echo "Testing put-pr.py"
./testserver.py traces/put-pr.trace &
put-pr.py -l inputs/put-pr.input -u 127.0.0.1 -p 8000 -r magnus.storsjo APPROVED > actual/put-pr.output
if [ $? -ne 2 ]
then
  echo "Failed testing put-pr.py"
  curl 127.0.0.1:8000/stop
  exit 1
fi
curl 127.0.0.1:8000/stop
diff -Zb expected/get-projects.output actual/get-projects.output
result=$?
test $result -eq 0 || echo "Failed test put-pr.py"
exit $result