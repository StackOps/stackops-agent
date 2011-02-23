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

echo "Welcome to StackOps: \s \v" > /etc/issue
echo "" >> /etc/issue
echo "To configure this node, connect to http://`LC_ALL=C ifconfig  | grep -m 1 'inet addr:'| cut -d: -f2 | awk '{print $1}'`:8888 " >> /etc/issue
echo "" >> /etc/issue
