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

SERVICE_TOKEN=999888777666
IMAGE_NAME='ttylinux-uec-amd64-12.1_2.6.35-22_1'
echo "Downloading images..."
wget http://stackops.s3.amazonaws.com/images/$IMAGE_NAME.tar.gz -O /tmp/$IMAGE_NAME.tar.gz

mkdir -p /tmp/images
tar -zxf /tmp/$IMAGE_NAME.tar.gz  -C /tmp/images

RVAL=`glance add -A $SERVICE_TOKEN name="ttylinux-kernel" is_public=true container_format=aki disk_format=aki < /tmp/images/$IMAGE_NAME-vmlinuz*`
KERNEL_ID=`echo $RVAL | cut -d":" -f2 | tr -d " "`
glance add -A $SERVICE_TOKEN name="ttylinux" is_public=true container_format=ami disk_format=ami kernel_id=$KERNEL_ID < /tmp/images/$IMAGE_NAME.img
