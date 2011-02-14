#!/usr/bin/env bash

rm -fR dist
mkdir dist
rm -fR build
mkdir build
cd build

cp -fR ../scripts/* .
cp -fR ../src/*.py var/lib/stackops/

tar cvf ../dist/stackops-agent.tar *
gzip ../dist/stackops-agent.tar
cd ..

rm -fR build
