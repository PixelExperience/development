"""Test nsjail."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import container
import mock


class ContainerTest(unittest.TestCase):

  @mock.patch('container.os.getcwd', return_value='/source_dir')
  @mock.patch('container.os.getuid', return_value=1)
  @mock.patch('container.os.getgid', return_value=2)
  @mock.patch('container.subprocess.check_call')
  def testBasic(self,
                mock_check_call,
                mock_getgid,
                mock_getuid,
                mock_getcwd):
    del mock_getgid, mock_getuid, mock_getcwd
    container.run(
        container_command='/bin/container_command',
        android_target='target_name')
    mock_check_call.assert_called_with([
        'docker', 'run',
        '--mount', 'type=bind,source=/source_dir,target=/src',
        '--tty',
        '--privileged',
        '--interactive',
        container._IMAGE,
        'python',
        '-B',
        '/src/development/keystone/nsjail.py',
        '--android_target', 'target_name',
        '--chroot', '/',
        '--source_dir', '/src',
        '--user_id', '1',
        '--group_id', '2',
        '--command', '/bin/container_command'
    ])


if __name__ == '__main__':
  unittest.main()
