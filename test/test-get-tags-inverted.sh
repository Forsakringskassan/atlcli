#!/usr/bin/sh
# set -x
echo "Testing atlcli bitb get-tags -n 'rc/.*' -i"
./testserver.py traces/get-tags-inverted.trace &
echo -e 'python-postgresql-patches\tIOS' | atlcli bitb get-tags -u 127.0.0.1 -p 8000 -n 'rc/.*' -i > actual/get-tags-inverted.output
if [ $? -ne 0 ]
then
  echo "Failed testing atlcli bitb get-tags -n 'rc/.*' -i"
  curl 127.0.0.1:8000/stop
  exit 1
fi
curl 127.0.0.1:8000/stop
diff -Zb expected/get-tags-inverted.output actual/get-tags-inverted.output
result=$?
test $result -eq 0 || echo "Failed test atlcli bitb get-tags -n 'rc/.*' -i"
exit $result