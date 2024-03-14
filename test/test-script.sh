#!/usr/bin/sh
# set -x
echo "Testing $1"
if test "$#" -lt 2;
then
  echo "Too few arguments"
  exit 1
elif test "$#" -gt 4;
then
  echo "Too many arguments"
  exit 1
elif test "$#" -gt 3;
then
  trace=$2
  input=$3
  output=$4
elif test "$#" -gt 2;
then
  trace=$2
  input=$2
  output=$3
elif test "$#" -gt 1;
then
  trace=$2
  input=$2
  output=$2
fi
./testserver.py traces/$trace.trace &
# echo $!
sleep 1
cat inputs/$input.input | $1 -u 127.0.0.1 -p 8000 > actual/$output.output
if [ $? -ne 0 ]
then
  echo "Failed testing $1 piping input"
  curl 127.0.0.1:8000/stop
  exit 1
fi
diff -ZbB expected/$output.output actual/$output.output
if [ $? -ne 0 ]
then
  echo "Failed diff testing $1 piping input"
  curl 127.0.0.1:8000/stop
  exit 1
fi
$1 -u 127.0.0.1 -p 8000 -l inputs/$input.input > actual/$output.output
if [ $? -ne 0 ]
then
  echo "Failed testing $1 giving input as parameter"
  curl 127.0.0.1:8000/stop
  exit 1
fi
curl 127.0.0.1:8000/stop
diff -ZbB expected/$output.output actual/$output.output
if [ $? -ne 0 ]
then
  echo "Failed diff testing $1 giving input as parameter"
  exit 1
fi
