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

if [ "$VERSION" == "" ]; then
echo "Sorry, VERSION environment variable not set. Exiting."
exit 1
fi

rm -fR dist
mkdir dist
rm -fR build
mkdir build
cd build

cp -fR ../scripts/* .
cp -fR ../src/*.py var/lib/stackops/
cp -fR ../src/*.conf var/lib/stackops/
cp -fR ../src/*.iptables var/lib/stackops/
cp -fR ../src/django.wsgi var/lib/stackops/
cp -fR ../src/acens.* var/lib/stackops/
chmod 700 var/lib/stackops/*.sh

tar cvf ../dist/stackops-agent-$VERSION.tar *
gzip ../dist/stackops-agent-$VERSION.tar
if [ "$DEV" != "true" ]; then
    s3cmd put --acl-public --guess-mime-type ../dist/stackops-agent-$VERSION.tar.gz s3://stackops/stackops-agent-$VERSION.tar.gz
fi

cd ..

rm -fR build
