# Keystone

This folder contains scripts used for building the keystone branch.

[TOC]

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

Downstream consumers of the Android platform often create independent Android
branches for each device.

We can unify the development of all devices from the same SoC family with the help
of filesystem overlays and specifically with OverlayFS. Here we shall focus on OverayFS
at a high level. See the 
[documentation on kernel.org](https://www.kernel.org/doc/Documentation/filesystems/overlayfs.txt)
for details on how OverlayFS works.

With OverlayFS we're able to dynamically select the set of projects
we want to build. This makes it possible to keep sets of
target specific projects while sharing common platform projects.

For example, if we had two devices: Device A and Device B the vendor overlays
would create the following build time views.

```
+-------------------------------+ +--------------------------------------------+
|         Android repo          | |                Android repo                |
|          workspace            | |                 workspace                  |
|                               | |                                            |
| +--------------+              | | +----------------------------------------+ |
| | +----------+ | +----------+ | | | +----------+  +----------+             | |
| | | Platform | | | Device B | | | | | Platform |  | Device B |   Device B  | |
| | | projects | | | projects | | | | | projects |  | projects |  build view | |
| | +----------+ | +----------+ | | | +----------+  +----------+             | |
| |              |              | | +----------------------------------------+ |
| | +----------+ |              | |   +----------+                             |
| | | Device A | |              | |   | Device A |                             |
| | | projects | |              | |   | projects |                             |
| | +----------+ |              | |   +----------+                             |
| |              |              | +--------------------------------------------+
| |   Device A   |              |
| |  build view  |              |
| |              |              |
| +--------------+              |
+-------------------------------+
```

The Android repo workspace is required to have a structure as follows.

### Root directory

Location: ${ANDROID_BUILD_TOP}

All projects in the root directory that are not in the overlays
directory are shared among all Android targets.

### Overlays directory

Location: ${ANDROID_BUILD_TOP}/overlays

Contains target specific projects. Each subdirectory under the overlays
directory can be mounted at the root directory to support different targets.
For example: the sdm845 Android target requires all the projects at
the root directory and the projects at
${ANDROID_BUILD_TOP}/overlays/qcom-LA.UM.7.3-incoming.

### Build out directory

Location: ${ANDROID_BUILD_TOP}/out

Contains all files generated during a build. This includes the target files
like system.img and host tools like adb.

### Overlay build directory

Location: ${ANDROID_BUILD_TOP}/out/overlays

Contains all files written to any location in the workspace other than
build out directory.  Most notably, some modules incorrectly attempt to
write files directly to a source directory. The overlay filesystem
redirects all attempts to write to the source directory to the overlay
build directory.

## Testing

To run a test just execute it in python like so:

```
python overlay_test.py
```
