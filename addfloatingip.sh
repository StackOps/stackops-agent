#!/bin/bash

HOST=$1
PORT=$2
USERNAME=$3
PASSWORD=$4
IP=$5
mysql -h$HOST --port=$PORT -u$USERNAME -p$PASSWORD -e "use nova; insert into floating_ips (created_at, deleted, address, auto_assigned) values (NOW(), 0, '$IP',0);"
