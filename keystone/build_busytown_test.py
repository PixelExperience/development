"""Test build_busytown."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import build_busytown
import mock


class BuildBusytownTest(unittest.TestCase):

  @mock.patch('build_busytown.os.getcwd', return_value='/source_dir')
  @mock.patch('build_busytown.nsjail.run')
  def testBasic(self, mock_nsjail_run, mock_getcwd):
    del mock_getcwd
    build_busytown.build(
        android_target='target_name',
        nsjail_bin='/bin/nsjail_bin',
        chroot='/chroot',
        dist_dir='/dist_dir',
        build_id='0',
        max_cpus=1)
    mock_nsjail_run.assert_called_with(
        android_target='target_name',
        build_id='0',
        chroot='/chroot',
        command=[
            '/src/development/keystone/build_keystone.sh',
            'target_name-userdebug',
            '/src',
            'make', '-j', 'droid', 'showcommands', 'dist', 'platform_tests'
        ],
        dist_dir='/dist_dir',
        max_cpus=1,
        nsjail_bin='/bin/nsjail_bin',
        source_dir='/source_dir')


if __name__ == '__main__':
  unittest.main()
