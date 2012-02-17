#!/bin/bash

USERNAME=$1
PASSWORD=$2
IP=$3
mysql -hlocalhost -u$USERNAME -p$PASSWORD -e "use nova; insert into floating_ips (created_at, deleted, address, auto_assigned) values (NOW(), 0, '$IP',0);" 
