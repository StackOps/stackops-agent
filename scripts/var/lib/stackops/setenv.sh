#!/usr/bin/env bash
# Heavily inspired in this: https://github.com/cloudbuilders/devstack/blob/master/openrc
# Thanks Vish!
#
HOST_IP=${HOST_IP:-127.0.0.1}
export NOVA_PROJECT_ID=${TENANT:-admin}
export NOVA_USERNAME=${USERNAME:-admin}
export NOVA_API_KEY=${ADMIN_PASSWORD:-password}
export NOVA_URL=${NOVA_URL:-http://$HOST_IP:5000/v2.0/}
export NOVA_VERSION=${NOVA_VERSION:-1.1}
export NOVA_REGION_NAME=${NOVA_REGION_NAME:-nova}
export NOVA_AUTH_STRATEGY=keystone
export EC2_URL=${EC2_URL:-http://$HOST_IP:80/services/Cloud}
export EC2_ACCESS_KEY=${USERNAME:-admin}
export EC2_SECRET_KEY=${ADMIN_PASSWORD:-password}
#export NOVACLIENT_DEBUG=1

export OS_AUTH_USER=$NOVA_USERNAME
export OS_AUTH_KEY=$NOVA_API_KEY
export OS_AUTH_TENANT=$NOVA_PROJECT_ID
export OS_AUTH_URL=$NOVA_URL
export OS_AUTH_STRATEGY=$NOVA_AUTH_STRATEGY

export AUTH_TOKEN=`curl -s -d "{\"auth\":{\"passwordCredentials\": {\"username\": \"$NOVA_USERNAME\", \"password\": \"$NOVA_API_KEY\"}, \"tenantName\": \"$NOVA_PROJECT_ID\"}}" -H "Content-type: application/json" http://$HOST_IP:5000/v2.0/tokens | python -c "import sys; import json; tok = json.loads(sys.stdin.read()); print tok['access']['token']['id'];"`
