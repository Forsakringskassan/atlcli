#!/usr/bin/sh
# set -x
echo "Testing atlcli tool select-columns"
cat inputs/select-columns.input | atlcli tool select-columns 4 3 2 1 0 > actual/select-columns.output
if [ $? -ne 0 ]
then
  echo "Failed testing atlcli tool select-columns"
  exit 1
fi
diff -Zb expected/select-columns.output actual/select-columns.output
result=$?
test $result -eq 0 || echo "Failed test atlcli tool select-columns"
exit $result