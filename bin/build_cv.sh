#!/usr/bin/env bash
mkdir -p build
cd build
make4ht -d ../docs/build_out/cv ../src/cv/main.tex
