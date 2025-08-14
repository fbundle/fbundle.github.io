#!/usr/bin/env bash
set -xe

mkdir -p build
cd build
make4ht -d ../docs/build_out/cv ../src/cv/main.tex
cd ..
rm -rf build
