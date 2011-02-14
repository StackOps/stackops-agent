#!/usr/bin/env bash

echo "Welcome to StackOps: \s \v" > /etc/issue
echo "" >> /etc/issue
echo "To configure this node, connect to http://`LC_ALL=C ifconfig  | grep -m 1 'inet addr:'| cut -d: -f2 | awk '{print $1}'`:8888 " >> /etc/issue
echo "" >> /etc/issue
