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

echo -n "Enter your admin user for Horizon: "
read user
echo -n "Enter your admin password for Horizon: "
read password

export ADMIN_USERNAME=$user
export ADMIN_PASSWORD=$password

echo $ADMIN_USERNAME $ADMIN_PASSWORD

exit 1
SCRIPTS_PATH=/var/lib/stackops

for i in `ls $SCRIPTS_PATH/pub*.sh|grep -v puball.sh`
do
	echo " Executing $i ..."
	bash $i
done
