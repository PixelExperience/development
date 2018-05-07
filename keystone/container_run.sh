#!/bin/bash

GID=$(id --group)
SOURCE_DIR=$PWD

# Use the NsJail sandbox by default
NSJAIL=/src/development/keystone/nsjail.py
DEFAULT_COMMAND="python $NSJAIL --chroot / --source_dir /src"

# The command may be provided as an argument
if [ -z $1 ]; then
  COMMAND=$DEFAULT_COMMAND
else
  COMMAND="$@"
fi

docker run \
  --user "$UID:$GID" \
  --mount "type=bind,source=$SOURCE_DIR,target=/src" \
  --tty \
  --privileged \
  --interactive \
  gcr.io/google.com/android-keystone-182020/android-build \
  $COMMAND
