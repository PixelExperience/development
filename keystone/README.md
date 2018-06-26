# Keystone

This folder contains scripts used for building the keystone branch.

## Setup

The keystone builder image provides all the host dependencies
you need to build Android. To set it up follow the instructions
below.

1. [Install Docker CE](https://www.docker.com/community-edition)

1. Build the Android build container:

   ```
   docker build --tag android-build development/keystone
   ```

## Building

Most developers just need to do the following:

```
python development/keystone/container.py
source build/envsetup.sh
lunch sdm845-userdebug
make -j
```

If you would like to build a target other than the default target then:

```
python development/keystone/container.py --android_target sdm660_64
source build/envsetup.sh
lunch sdm660_64-userdebug
make -j
```

## Busytown builds

Busytown builds (aka go/ab) invoke the ```build_busytown_*.py``` scripts contained
in this directory. These builds support NsJail but not docker containers.
Instead they provide a chroot with all the Android build host dependencies.

## Docker container builds

Google platform engineers build inside a docker container. The container.py
script in this directory sets up such container. The dockerfile for the
container is also provided.

## NsJail sandbox

Both Busytown builds and Docker container builds create an NsJail sandbox via
nsjail.py and nsjail.cfg. The purpose of the sandbox is to provide secure
process isolation.

## Vendor overlays

By using OverlayFS we're able to dynamically select from multiple vendor project
sets within the same source tree. This is implemented in overlay.py.

## Testing

To run a test just execute it in python like so:

```
python overlay_test.py
```
