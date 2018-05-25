"""Test overlay."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import shutil
import subprocess
import tempfile
import unittest
import overlay


class MountTest(unittest.TestCase):

  def testCreate(self):
    mount = overlay.Mount(
        mount_command=['/bin/true'],
        unmount_command=['/bin/true'])
    self.assertEqual(
        mount.mount_command,
        ['/bin/true']
    )

  def testFailedMount(self):
    with self.assertRaises(subprocess.CalledProcessError):
      overlay.Mount(
          mount_command=['/bin/false'],
          unmount_command=['/bin/true']
      )

  def testDelete(self):
    tempdir = tempfile.mkdtemp()
    try:
      unmount_file = os.path.join(tempdir, 'unmounted')
      overlay.Mount(
          mount_command=['/bin/true'],
          unmount_command=['/bin/touch', unmount_file])

      self.assertTrue(os.path.exists(unmount_file))
    finally:
      shutil.rmtree(tempdir)


class OverlayTest(unittest.TestCase):

  class FakeMount(object):

    def __init__(self, mount_command, unmount_command):
      self.mount_command = mount_command
      self.unmount_command = unmount_command

  def setUp(self):
    overlay.Mount = self.FakeMount
    self.source_dir = tempfile.mkdtemp()
    os.mkdir(os.path.join(self.source_dir, 'overlays'))
    os.mkdir(os.path.join(self.source_dir,
                          'overlays', 'qcom-LA.UM.7.3-incoming'))

  def tearDown(self):
    shutil.rmtree(self.source_dir)

  def testCreateFromValidTarget(self):
    o = overlay.Overlay(
        target='sdm845',
        source_dir=self.source_dir)
    self.assertIsNotNone(o)
    mounts = o.GetMountInfo()
    unmount_commands = [mount['unmount_command'] for mount in mounts]
    self.assertIn(
        ['sudo', 'umount', os.path.join(self.source_dir)],
        unmount_commands
    )
    self.assertIn(
        ['sudo', 'umount', os.path.join(self.source_dir, 'out')],
        unmount_commands
    )

  def testInvalidTarget(self):
    with self.assertRaises(KeyError):
      overlay.Overlay(
          target='unknown',
          source_dir='/source_dir')


if __name__ == '__main__':
  unittest.main()
