"""Test nsjail."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import subprocess
import unittest
import nsjail


class NsjailTest(unittest.TestCase):

  def setUp(self):
    nsjail.__file__ = '/'

  def testMinimalParameters(self):
    commands = nsjail.run(
        nsjail_bin='/bin/true',
        chroot='/chroot',
        source_dir='/source_dir',
        command=['/bin/bash'],
        android_target='target_name')
    self.assertEqual(
        commands,
        [
            [
                '/bin/true',
                '--bindmount', '/source_dir:/src',
                '--chroot', '/chroot',
                '--env', 'USER=android-build',
                '--config', '/nsjail.cfg',
                '--', '/bin/bash'
            ]
        ]
    )

  def testFailingJailedCommand(self):
    with self.assertRaises(subprocess.CalledProcessError):
      nsjail.run(
          nsjail_bin='/bin/false',
          chroot='/chroot',
          source_dir='/source_dir',
          command=['/bin/bash'],
          android_target='target_name')

  def testDist(self):
    commands = nsjail.run(
        nsjail_bin='/bin/true',
        chroot='/chroot',
        source_dir='/source_dir',
        command=['/bin/bash'],
        android_target='target_name',
        dist_dir='/dist_dir')
    self.assertEqual(
        commands,
        [
            [
                '/bin/true',
                '--bindmount', '/source_dir:/src',
                '--chroot', '/chroot',
                '--env', 'USER=android-build',
                '--config', '/nsjail.cfg',
                '--bindmount', '/dist_dir:/dist',
                '--env', 'DIST_DIR=/dist',
                '--', '/bin/bash'
            ]
        ]
    )

  def testBuildID(self):
    commands = nsjail.run(
        nsjail_bin='/bin/true',
        chroot='/chroot',
        source_dir='/source_dir',
        command=['/bin/bash'],
        android_target='target_name',
        build_id='0')
    self.assertEqual(
        commands,
        [
            [
                '/bin/true',
                '--bindmount', '/source_dir:/src',
                '--chroot', '/chroot',
                '--env', 'USER=android-build',
                '--config', '/nsjail.cfg',
                '--env', 'BUILD_NUMBER=0',
                '--', '/bin/bash'
            ]
        ]
    )

  def testMaxCPU(self):
    commands = nsjail.run(
        nsjail_bin='/bin/true',
        chroot='/chroot',
        source_dir='/source_dir',
        command=['/bin/bash'],
        android_target='target_name',
        max_cpus=1)
    self.assertEqual(
        commands,
        [
            [
                '/bin/true',
                '--bindmount', '/source_dir:/src',
                '--chroot', '/chroot',
                '--env', 'USER=android-build',
                '--config', '/nsjail.cfg',
                '--max_cpus=1',
                '--', '/bin/bash'
            ]
        ]
    )

  def testUserGroupID(self):
    nsjail.GROUPADD_COMMAND = '/bin/true'
    nsjail.USERADD_COMMAND = '/bin/true'
    commands = nsjail.run(
        nsjail_bin='/bin/true',
        chroot='/chroot',
        source_dir='/source_dir',
        command=['/bin/bash'],
        android_target='target_name',
        user_id=os.getuid(),
        group_id=os.getgid())
    self.assertEqual(
        commands,
        [
            [
                '/bin/true',
                'android-build',
                '--gid', str(os.getgid()),
            ],
            [
                '/bin/true',
                '--gid', 'android-build',
                '--groups', 'sudo',
                '--uid', str(os.getuid()),
                '--create-home',
                'android-build'
            ],
            [
                '/bin/true',
                '--bindmount', '/source_dir:/src',
                '--chroot', '/chroot',
                '--env', 'USER=android-build',
                '--config', '/nsjail.cfg',
                '--', '/bin/bash'
            ]
        ]
    )


if __name__ == '__main__':
  unittest.main()
