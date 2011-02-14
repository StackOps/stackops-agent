#!/usr/bin/env bash

rm -fR dist
mkdir dist
rm -fR build
mkdir -p build/var/lib/stackops
cd build

cp -fR ../scripts/* .
cp -fR ../src/*.py var/lib/stackops/

tar cvfz ../dist/stackops-agent.tgz *
cd ..

rm -fR build
