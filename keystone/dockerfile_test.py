"""Test the dockerfile."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import subprocess
import unittest


class DockerfileTest(unittest.TestCase):

  def testRepoTool(self):
    subprocess.check_call(['repo', 'help', 'init'])

  def testNsJail(self):
    subprocess.check_call([
        '/bin/nsjail',
        '--config', '/usr/share/android-build.cfg',
        '--chroot', '/',
        '--', '/bin/true'
    ])


if __name__ == '__main__':
  unittest.main()
