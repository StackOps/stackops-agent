#   Copyright 2011 STACKOPS TECHNOLOGIES S.L.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#!/usr/bin/env bash

# Original code from www.devstack.org

HOST_IP=${HOST:-127.0.0.1}
NOVA_TENANT_ID=${TENANT:-1}
NOVA_USERNAME=${USERNAME:-admin}
NOVA_API_KEY=${ADMIN_PASSWORD:-password}

SERVICE_TOKEN=`curl -s -d "{\"auth\":{\"passwordCredentials\": {\"username\": \"$NOVA_USERNAME\", \"password\": \"$NOVA_API_KEY\"}, \"tenantId\": \"$NOVA_TENANT_ID\"}}" -H "Content-type: application/json" http://$HOST_IP:5000/v2.0/tokens | python -c "import sys; import json; tok = json.loads(sys.stdin.read()); print tok['access']['token']['id'];"`

IMAGE_NAME='centos-5.7-x86_64.img'
echo "Downloading images..."
wget http://stackops.s3.amazonaws.com/images/$IMAGE_NAME.tar.gz -O /tmp/$IMAGE_NAME.tar.gz

mkdir -p /tmp/images
tar -zxf /tmp/$IMAGE_NAME.tar.gz  -C /tmp/images

glance add -A $SERVICE_TOKEN name="$IMAGE_NAME" is_public=true container_format=bare disk_format=qcow2  < /tmp/images/$IMAGE_NAME
