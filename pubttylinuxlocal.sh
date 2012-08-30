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
NOVA_USERNAME=${USERNAME:-admin}
NOVA_PASSWORD=${ADMIN_PASSWORD:-password}

IMAGE_NAME='ttylinux-uec-amd64-12.1_2.6.35-22_1'

RVAL=`glance add  --silent-upload --os_username=$NOVA_USERNAME --os_password=$NOVA_PASSWORD --os_tenant_name=$NOVA_TENANT_NAME --os_auth_url=http://$HOST_IP:5000/v2.0/ name="ttylinux-uec-amd64-kernel" is_public=true container_format=aki disk_format=aki < /var/lib/stackops/$IMAGE_NAME-vmlinuz*`
KERNEL_ID=`echo $RVAL | cut -d":" -f2 | tr -d " "`
glance add --os_username=$NOVA_USERNAME --os_password=$NOVA_PASSWORD --os_tenant_name=$NOVA_TENANT_NAME --os_auth_url=http://$HOST_IP:5000/v2.0/ name="ttylinux-uec-amd64" is_public=true container_format=ami disk_format=ami kernel_id=$KERNEL_ID < /var/lib/stackops/$IMAGE_NAME.img
