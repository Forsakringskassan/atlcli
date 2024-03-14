#!/usr/bin/sh
# set -x
echo "Testing atlcli bitb get-branches-or-tags -n dummy -i"
./testserver.py traces/get-branches-or-tags-inverted.trace &
echo -e 'python-postgresql-patches\tIOS' | atlcli bitb get-branches-or-tags -u 127.0.0.1 -p 8000 -n dummy -i > actual/get-branches-or-tags-inverted.output
if [ $? -ne 0 ]
then
  echo "Failed testing atlcli bitb get-branches-or-tags -n dummy -i"
  curl 127.0.0.1:8000/stop
  exit 1
fi
curl 127.0.0.1:8000/stop
diff -Zb expected/get-branches-or-tags-inverted.output actual/get-branches-or-tags-inverted.output
result=$?
test $result -eq 0 || echo "Failed testing atlcli bitb get-branches-or-tags -n dummy -i"
exit $result