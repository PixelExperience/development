"""Apply filesystem overlays.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import subprocess


class Overlay(object):
  """Manages filesystem overlays of Android source tree.
  """
  # TODO(diegowilson): Add gms overlay
  BRANCH_MAP = {
      'sdm845': 'qcom-LA.UM.7.3-incoming',
      'sdm660_64': 'qcom-LA.UM.7.2-incoming',
  }

  def _apply(self, source_dir, overlay_dir):
    """Applies the selected overlay directory.

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
    """
    lowerdirs = [
        overlay_dir,
        source_dir,
    ]
    workdir = os.path.join(source_dir, 'overlays', 'work')

    upperdir = os.path.join(source_dir, 'overlays', 'artifacts')

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
    # Only save the source directories until
    # we have succesfully applied the overlay to avoid
    # attempting an unmount if the mount failed.
    self.source_dir = source_dir
    self.overlay_dir = overlay_dir
    print('Applied overlay ' + self.overlay_dir)

  def _strip(self):
    """Strips out all applied overlays.
    """
    if self.source_dir:
      command = ['sudo', 'umount', os.path.abspath(self.source_dir)]
      subprocess.check_call(command)
    if self.overlay_dir:
      print('Stripped out overlay ' + self.overlay_dir)

  def __init__(self, target, source_dir):
    """Inits Overlay with the details of what is going to be overlaid.

    Args:
      target: A string with the name of the target to be prepared.
      source_dir: A string with the path to the Android platform source.
    """
    self.source_dir = None
    self.overlay_dir = None
    branch = self.BRANCH_MAP[target]
    overlay_dir = os.path.join(source_dir, 'overlays', branch)

    # Create an empty overlays file to white out overlays dir.
    # Otherwise the build system will try to detect all
    # the Android.bp and Android.mk modules under the overlays
    # dir and conflict with the ovelays applied at the top.
    overlay_whiteout = os.path.join(overlay_dir, 'overlays')
    open(overlay_whiteout, 'a').close()

    self._apply(source_dir, overlay_dir)

  def __del__(self):
    """Cleans up Overlay.
    """
    self._strip()
