"""Mounts all the projects required by a selected Android target.

For details on how vendor overlays work see the vendor overlays
section of the README.md.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import subprocess
import tempfile


class Mount(object):
  """Manages a filesystem mount.
  """

  def __init__(self, mount_command, unmount_command):
    self.mount_command = None
    self.unmount_command = None
    subprocess.check_call(mount_command)
    self.mount_command = mount_command
    self.unmount_command = unmount_command

  def __del__(self):
    if self.unmount_command:
      subprocess.check_call(self.unmount_command)


class Overlay(object):
  """Manages filesystem overlays of Android source tree.
  """
  OVERLAY_MAP = {
      'sdm845': ['qcom-LA.UM.7.3-incoming', 'keystone'],
      'sdm845_gms': ['qcom-LA.UM.7.3-incoming', 'gms', 'keystone'],
      'sdm660_64': ['qcom-LA.UM.7.2-incoming', 'keystone'],
      'cuttlestone': ['keystone'],
  }

  def _MountOverlay(self, source_dir, overlay_dirs, target):
    """Mounts the selected overlay directory.

    OverlayFS creates a merge directory composed of a union
    of source_dir and the overlay_dirs. Then source_dir is replaced
    by the resulting merge directory.

    OverlayFS also needs two new directories: upperdir and workdir.

    upperdir stores any files written to the merge directory.
    This is located in overlays/artifacts.

    workdir is a temporary working cache required by OverlayFS.
    This is located in overlays/work.

    Args:
      source_dir: A string with the path to the Android platform source.
      overlay_dirs: A list of strings with the paths to the overlay
        directory to apply.
      target: A string with the name of the target to be prepared.
    """
    lowerdirs = overlay_dirs
    lowerdirs.append(source_dir)

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

    mount_command = [
        'sudo', 'mount',
        '--types', 'overlay',
        '--options', mount_options,
        'overlay',
        source_dir
    ]
    unmount_command = ['sudo', 'umount', source_dir]
    self._AddMount(mount_command, unmount_command)

  def _AddMount(self, mount_command, unmount_command):
    mount = Mount(
        mount_command=mount_command,
        unmount_command=unmount_command)
    self._mounts.append(mount)

  def GetMountInfo(self):
    """Gets details on the filesystem devices mounted.

    Returns:
      A list of dicts. Each dict entry represents a device mounted
      with the following fields:
        mount_command: A list of strings with the command that was
          used for mounting.
        unmount_command: A list of strings with the command that will
          be used for unmounting.
    """
    mount_info = [{'mount_command': mount.mount_command,
                   'unmount_command': mount.unmount_command}
                  for mount in self._mounts]
    return mount_info

  def __init__(self, target, source_dir):
    """Inits Overlay with the details of what is going to be overlaid.

    Args:
      target: A string with the name of the target to be prepared.
      source_dir: A string with the path to the Android platform source.
    """
    self._overlay_dirs = None
    self._mounts = []

    # Save a reference to the workspace out directory
    out_dir = os.path.join(source_dir, 'out')
    if not os.path.exists(out_dir):
      os.mkdir(out_dir)
    original_out_dir = tempfile.mkdtemp()
    self._AddMount(['sudo', 'mount', '--bind', out_dir, original_out_dir],
                   ['sudo', 'umount', original_out_dir])

    overlay_dirs = []
    for overlay_dir in self.OVERLAY_MAP[target]:
      overlay_dir = os.path.join(source_dir, 'overlays', overlay_dir)

      # Create an empty overlays file to white out overlays dir.
      # Otherwise the build system will try to detect all
      # the Android.bp and Android.mk modules under the overlays
      # dir and conflict with the ovelays applied at the top.
      overlay_whiteout = os.path.join(overlay_dir, 'overlays')
      open(overlay_whiteout, 'a').close()
      overlay_dirs.append(overlay_dir)

    self._MountOverlay(source_dir, overlay_dirs, target)
    self._overlay_dirs = overlay_dirs
    print('Applied overlays ' + ' '.join(self._overlay_dirs))

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

    self._AddMount(['sudo', 'mount', '--bind', original_out_dir, out_dir],
                   ['sudo', 'umount', out_dir])

  def __del__(self):
    """Cleans up Overlay.
    """
    if self._overlay_dirs:
      print('Stripped out overlay ' + ' '.join(self._overlay_dirs))
