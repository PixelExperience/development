"""Mounts all the projects required by a selected Android target.

The repo workspace is required to have the following structure:

Root directory
Location: ${ANDROID_BUILD_TOP}
All projects in the root directory that are not in the overlays
directory are shared among all Android targets.

Overlays directory
Location: ${ANDROID_BUILD_TOP}/overlays
Contains target specific projects. Each subdirectory under the overlays
directory can be mounted at the root directory to support different targets.
For example: the sdm845 Android target requires all the projects at
the root directory and the projects at
${ANDROID_BUILD_TOP}/overlays/qcom-LA.UM.7.3-incoming.

Build out directory
Location: ${ANDROID_BUILD_TOP}/out
Contains all files generated during a build. This includes the target files
like system.img and host tools like adb.

Overlay build directory
Location: ${ANDROID_BUILD_TOP}/out/overlays
Contains all files written to any location in the workspace other than
build out directory.  Most notably, some modules incorrectly attempt to
write files directly to a source directory. The overlay filesystem
redirects all attempts to write to the source directory to the overlay
build directory.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import subprocess
import tempfile


class Overlay(object):
  """Manages filesystem overlays of Android source tree.
  """
  # TODO(diegowilson): Add gms overlay
  BRANCH_MAP = {
      'sdm845': 'qcom-LA.UM.7.3-incoming',
      'sdm660_64': 'qcom-LA.UM.7.2-incoming',
  }

  def _MountOverlay(self, source_dir, overlay_dir, target):
    """Mounts the selected overlay directory.

    OverlayFS creates a merge directory composed of a union
    of source_dir and the overlay_dir. Then source_dir is replaced
    by the resulting merge directory.

    OverlayFS also needs two new directories: upperdir and workdir.

    upperdir stores any files written to the merge directory.
    This is located in overlays/artifacts.

    workdir is a temporary working cache required by OverlayFS.
    This is located in overlays/work.

    Args:
      source_dir: A string with the path to the Android platform source.
      overlay_dir: A string with the path to the overlay directory to
        apply.
      target: A string with the name of the target to be prepared.
    """
    lowerdirs = [
        overlay_dir,
        source_dir,
    ]
    overlay_out_dir = os.path.join(source_dir, 'out', 'overlays')
    target_out_dir = os.path.join(overlay_out_dir, target)
    workdir = os.path.join(target_out_dir, 'work')
    upperdir = os.path.join(target_out_dir, 'artifacts')

    if not os.path.isdir(overlay_out_dir):
      os.mkdir(overlay_out_dir)
    if not os.path.isdir(target_out_dir):
      os.mkdir(target_out_dir)
    if not os.path.isdir(workdir):
      os.mkdir(workdir)
    if not os.path.isdir(upperdir):
      os.mkdir(upperdir)

    mount_options = 'lowerdir=%s,' % ':'.join(lowerdirs)
    mount_options += 'upperdir=%s,' % upperdir
    mount_options += 'workdir=%s' % workdir

    command = [
        'sudo', 'mount',
        '--types', 'overlay',
        '--options', mount_options,
        'overlay',
        source_dir
    ]
    subprocess.check_call(command)
    # Only save the source directories after
    # we have succesfully applied the overlay to avoid
    # attempting an unmount if the mount failed.
    self._source_dir = source_dir
    self._overlay_dir = overlay_dir
    print('Applied overlay ' + self._overlay_dir)

  def _UnmountAll(self):
    """Unmounts everything mounted by this class.
    """
    if self._out_dir:
      subprocess.check_call([
          'sudo', 'umount', os.path.abspath(self._out_dir)
      ])
    if self.original_out_dir:
      subprocess.check_call([
          'sudo', 'umount', os.path.abspath(self.original_out_dir)
      ])
      os.rmdir(self.original_out_dir)
    if self._source_dir:
      subprocess.check_call([
          'sudo', 'umount', os.path.abspath(self._source_dir)
      ])
    if self._overlay_dir:
      print('Stripped out overlay ' + self._overlay_dir)

  def __init__(self, target, source_dir):
    """Inits Overlay with the details of what is going to be overlaid.

    Args:
      target: A string with the name of the target to be prepared.
      source_dir: A string with the path to the Android platform source.
    """
    self._source_dir = None
    self._overlay_dir = None
    self._out_dir = None
    self.original_out_dir = None
    branch = self.BRANCH_MAP[target]
    overlay_dir = os.path.join(source_dir, 'overlays', branch)

    # Create an empty overlays file to white out overlays dir.
    # Otherwise the build system will try to detect all
    # the Android.bp and Android.mk modules under the overlays
    # dir and conflict with the ovelays applied at the top.
    overlay_whiteout = os.path.join(overlay_dir, 'overlays')
    open(overlay_whiteout, 'a').close()

    # Save a reference to the workspace out directory
    out_dir = os.path.join(source_dir, 'out')
    if not os.path.exists(out_dir):
      os.mkdir(out_dir)
    self.original_out_dir = tempfile.mkdtemp()
    subprocess.check_call([
        'sudo', 'mount', '--bind', out_dir, self.original_out_dir
    ])

    self._MountOverlay(source_dir, overlay_dir, target)

    # Now that we've applied an overlay any files written
    # under the repo workspace root directory will be redirected
    # to out/overlays/artifacts. This is is fine for any misbehaving
    # modules attempting to write to the source during a build.
    # However, any modules attempting to write directly to out
    # during a build should be allowed to do so.
    #
    # Lucky for us we saved a reference to the original out file system
    # node. Now all we have to do is bind the saved reference
    # back to out and that will take precedence over the
    # overlay filesystem.

    subprocess.check_call([
        'sudo', 'mount', '--bind', self.original_out_dir, out_dir
    ])
    self._out_dir = out_dir

  def __del__(self):
    """Cleans up Overlay.
    """
    self._UnmountAll()
