#!/bin/bash

readonly ANDROID_TARGET=$1
readonly BUILD_DIR=$2
shift
shift
readonly BUILD_COMMAND="$@"

if [[ -z "${ANDROID_TARGET}" ]]; then
  echo "error: Android target not set"
  exit 1
fi

if [[ -z "${BUILD_DIR}" ]]; then
  echo "error: Build directory not set"
  exit 1
fi

if [[ -z "${BUILD_COMMAND}" ]]; then
  echo "error: Build command not set"
  exit 1
fi

source build/envsetup.sh
lunch "$ANDROID_TARGET"
cd "$BUILD_DIR"
$BUILD_COMMAND
