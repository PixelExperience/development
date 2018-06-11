"""Test build_busytown."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import unittest
import build_busytown


class BuildBusytownTest(unittest.TestCase):

  def testBasic(self):
    build_busytown.nsjail.__file__ = '/'
    os.chdir('/')
    commands = build_busytown.build(
        'target_name',
        'userdebug',
        nsjail_bin='/bin/true',
        chroot='/chroot',
        dist_dir='/dist_dir',
        build_id='0',
        max_cpus=1)

    self.assertEqual(
        commands,
        [
            [
                '/bin/true',
                '--bindmount', '/:/src',
                '--chroot', '/chroot',
                '--env', 'USER=android-build',
                '--config', '/nsjail.cfg',
                '--bindmount', '/dist_dir:/dist',
                '--env', 'DIST_DIR=/dist',
                '--env', 'BUILD_NUMBER=0',
                '--max_cpus=1',
                '--',
                '/src/development/keystone/build_keystone.sh',
                'target_name-userdebug',
                '/src',
                'make', '-j', 'droid', 'showcommands', 'dist', 'platform_tests'
            ]
        ]
    )

  def testUser(self):
    build_busytown.nsjail.__file__ = '/'
    os.chdir('/')
    commands = build_busytown.build(
        'target_name',
        'user',
        nsjail_bin='/bin/true',
        chroot='/chroot',
        dist_dir='/dist_dir',
        build_id='0',
        max_cpus=1)

    self.assertEqual(
        commands,
        [
            [
                '/bin/true',
                '--bindmount', '/:/src',
                '--chroot', '/chroot',
                '--env', 'USER=android-build',
                '--config', '/nsjail.cfg',
                '--bindmount', '/dist_dir:/dist',
                '--env', 'DIST_DIR=/dist',
                '--env', 'BUILD_NUMBER=0',
                '--max_cpus=1',
                '--',
                '/src/development/keystone/build_keystone.sh',
                'target_name-user',
                '/src',
                'make', '-j', 'droid', 'showcommands', 'dist', 'platform_tests'
            ]
        ]
    )


if __name__ == '__main__':
  unittest.main()
