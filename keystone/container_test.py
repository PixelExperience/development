"""Test nsjail."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import unittest
import container


class ContainerTest(unittest.TestCase):

  def testBasic(self):
    os.chdir('/')
    commands = container.run(
        container_command='/bin/container_command',
        android_target='target_name',
        docker_bin='/bin/true')
    self.assertEqual(
        commands,
        [
            '/bin/true', 'run',
            '--mount', 'type=bind,source=/,target=/src',
            '--tty',
            '--privileged',
            '--interactive',
            'android-build',
            'python',
            '-B',
            '/src/development/keystone/nsjail.py',
            '--android_target', 'target_name',
            '--chroot', '/',
            '--source_dir', '/src',
            '--user_id', str(os.getuid()),
            '--group_id', str(os.getgid()),
            '--command', '/bin/container_command'
        ]
    )


if __name__ == '__main__':
  unittest.main()
