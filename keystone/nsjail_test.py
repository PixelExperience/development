"""Test nsjail."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import mock
import nsjail


class NsjailTest(unittest.TestCase):

  @mock.patch('nsjail.os.path.dirname', return_value='/')
  @mock.patch('nsjail.subprocess.check_call')
  def testMinimalParameters(self, mock_check_call, mock_dirname):
    del mock_dirname
    nsjail.run(
        nsjail_bin='/bin/nsjail',
        chroot='/chroot',
        source_dir='/source_dir',
        command=['/bin/bash'],
        android_target='target_name')
    mock_check_call.assert_called_with([
        '/bin/nsjail',
        '--bindmount', '/source_dir:/src',
        '--chroot', '/chroot',
        '--env', 'USER=android-build',
        '--config', '/nsjail.cfg',
        '--', '/bin/bash'
    ])

  @mock.patch('nsjail.os.path.dirname', return_value='/')
  @mock.patch('nsjail.subprocess.check_call')
  def testDist(self, mock_check_call, mock_dirname):
    del mock_dirname
    nsjail.run(
        nsjail_bin='/bin/nsjail',
        chroot='/chroot',
        source_dir='/source_dir',
        command=['/bin/bash'],
        android_target='target_name',
        dist_dir='/dist_dir')
    mock_check_call.assert_called_with([
        '/bin/nsjail',
        '--bindmount', '/source_dir:/src',
        '--chroot', '/chroot',
        '--env', 'USER=android-build',
        '--config', '/nsjail.cfg',
        '--bindmount', '/dist_dir:/dist',
        '--env', 'DIST_DIR=/dist',
        '--', '/bin/bash'
    ])

  @mock.patch('nsjail.os.path.dirname', return_value='/')
  @mock.patch('nsjail.subprocess.check_call')
  def testBuildID(self, mock_check_call, mock_dirname):
    del mock_dirname
    nsjail.run(
        nsjail_bin='/bin/nsjail',
        chroot='/chroot',
        source_dir='/source_dir',
        command=['/bin/bash'],
        android_target='target_name',
        build_id='0')
    mock_check_call.assert_called_with([
        '/bin/nsjail',
        '--bindmount', '/source_dir:/src',
        '--chroot', '/chroot',
        '--env', 'USER=android-build',
        '--config', '/nsjail.cfg',
        '--env', 'BUILD_NUMBER=0',
        '--', '/bin/bash'
    ])

  @mock.patch('nsjail.os.path.dirname', return_value='/')
  @mock.patch('nsjail.subprocess.check_call')
  def testMaxCPU(self, mock_check_call, mock_dirname):
    del mock_dirname
    nsjail.run(
        nsjail_bin='/bin/nsjail',
        chroot='/chroot',
        source_dir='/source_dir',
        command=['/bin/bash'],
        android_target='target_name',
        max_cpus=1)
    mock_check_call.assert_called_with([
        '/bin/nsjail',
        '--bindmount', '/source_dir:/src',
        '--chroot', '/chroot',
        '--env', 'USER=android-build',
        '--config', '/nsjail.cfg',
        '--max_cpus=1',
        '--', '/bin/bash'
    ])

  @mock.patch('nsjail.os.setgid')
  @mock.patch('nsjail.os.setuid')
  @mock.patch('nsjail.os.path.dirname', return_value='/')
  @mock.patch('nsjail.subprocess.check_call')
  def testUserGroupID(self,
                      mock_check_call,
                      mock_dirname,
                      mock_setuid,
                      mock_setgid):
    del mock_dirname, mock_setuid, mock_setgid
    nsjail.run(
        nsjail_bin='/bin/nsjail',
        chroot='/chroot',
        source_dir='/source_dir',
        command=['/bin/bash'],
        android_target='target_name',
        user_id=1,
        group_id=2)
    mock_check_call.assert_called_with([
        '/bin/nsjail',
        '--bindmount', '/source_dir:/src',
        '--chroot', '/chroot',
        '--env', 'USER=android-build',
        '--config', '/nsjail.cfg',
        '--', '/bin/bash'
    ])


if __name__ == '__main__':
  unittest.main()
