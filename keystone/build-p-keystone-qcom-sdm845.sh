#!/bin/bash

export PATH
export USER=android-build
cd /src
source build/envsetup.sh
lunch sdm845-userdebug
make -j droid showcommands dist platform_tests
