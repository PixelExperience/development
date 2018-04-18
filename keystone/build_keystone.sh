#!/bin/bash

TARGET=$1

if [ -z $TARGET ]; then
  echo "error: target not set"
  exit 1
fi

# TODO(diegowilson): do we still need this export?
export PATH
cd /src
source build/envsetup.sh
lunch $TARGET
make -j droid showcommands dist platform_tests
