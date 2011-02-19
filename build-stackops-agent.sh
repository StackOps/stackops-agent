#!/usr/bin/env bash

VERSION=0.0.1

rm -fR dist
mkdir dist
rm -fR build
mkdir build
cd build

cp -fR ../scripts/* .
cp -fR ../src/*.py var/lib/stackops/

tar cvf ../dist/stackops-agent-$VERSION.tar *
gzip ../dist/stackops-agent-$VERSION.tar
cd ..

rm -fR build
