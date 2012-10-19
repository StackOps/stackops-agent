#!/usr/bin/env bash

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

# Original code from www.devstack.org

HOST_IP=${HOST:-127.0.0.1}
NOVA_TENANT_NAME=${TENANT:-admin}
NOVA_USERNAME=${ADMIN_USERNAME:-admin}
NOVA_PASSWORD=${ADMIN_PASSWORD:-password}

IMAGE_NAME='centos-6.2-x86_64.img'
echo "Downloading images..."
wget http://stackops.s3.amazonaws.com/images/$IMAGE_NAME.tar.gz -O /tmp/$IMAGE_NAME.tar.gz

mkdir -p /tmp/images
tar -zxf /tmp/$IMAGE_NAME.tar.gz  -C /tmp/images

glance add --os_username=$NOVA_USERNAME --os_password=$NOVA_PASSWORD --os_tenant_name=$NOVA_TENANT_NAME --os_auth_url=http://$HOST_IP:5000/v2.0/ name="$IMAGE_NAME" is_public=true container_format=bare disk_format=qcow2  < /tmp/images/$IMAGE_NAME
