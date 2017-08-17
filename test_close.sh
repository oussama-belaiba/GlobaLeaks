#!/bin/bash

#set -x
#set -e

TT=`tty`
BASE='http://localhost:8082'

printf 'Logging into service %s\n\n' $BASE

read session_id < <(curl -s -A 'test-script' \
     -X POST -H 'Content-type: application/json' \
     -d '{"password": "nn2@n.org","username":"admin"}' \
     $BASE/authentication | tee -p $TT | python -c 'import json, sys; print(json.loads(sys.stdin.read())["session_id"]);'
  )

printf '\nAcquired session_id: %s\n' $session_id

curl -A 'test-script' -kis \
     -H "X-Session: $session_id" \
     -X POST -H 'Content-type: application/json' \
     -d '{"enabled": true}' \
     "$BASE/admin/config/tls"

sleep 5

# curl -A 'test-script' \
#      -kis https://localhost:8443/robots.txt > /dev/null &
# 
# curl -A 'test-script' \
#      -kis https://localhost:8443/robots.txt > /dev/null &
# 
# curl -A 'test-script' \
#      -kis https://localhost:8443/robots.txt > /dev/null &

printf '\nRunning large file dl\n\n'

curl -A 'test-script' \
     -kis https://localhost:8443/big.png -o /tmp/big.png &

sleep 5

printf '\nTurning off subprocs\n\n'

curl -A 'test-script' -kis \
     -H "X-Session: $session_id" \
     -X PUT -H 'Content-type: application/json' \
     -d '{"enabled": false}' \
     "$BASE/admin/config/tls"

# printf '\nRequesting new resource over TLS\n\n'
# 
# sleep 3
# 
# curl -A -vvv 'test-script' \
#      -kis https://localhost:8443/robots.txt
