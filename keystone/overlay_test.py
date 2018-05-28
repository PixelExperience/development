"""Test overlay."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import mock
import overlay


class OverlayTest(unittest.TestCase):

  @mock.patch('overlay.os.mkdir')
  @mock.patch('overlay.open')
  @mock.patch('overlay.subprocess.check_call')
  def testCreateFromValidTarget(self,
                                mock_check_call,
                                mock_open,
                                mock_mkdir):
    del mock_open, mock_mkdir
    o = overlay.Overlay(
        target='sdm845',
        source_dir='/source_dir')
    self.assertIsNotNone(o)
    mock_check_call.assert_called_with([
        'sudo', 'mount',
        '--types', 'overlay',
        '--options',
        ','.join([
            'lowerdir=/source_dir/overlays/qcom-LA.UM.7.3-incoming:/source_dir',
            'upperdir=/source_dir/overlays/artifacts',
            'workdir=/source_dir/overlays/work'
        ]),
        'overlay',
        '/source_dir'
    ])

  @mock.patch('overlay.os.mkdir')
  @mock.patch('overlay.open')
  @mock.patch('overlay.subprocess.check_call')
  def testDeleteFromValidTarget(self,
                                mock_check_call,
                                mock_open,
                                mock_mkdir):
    del mock_open, mock_mkdir
    o = overlay.Overlay(
        target='sdm845',
        source_dir='/source_dir')
    del o
    mock_check_call.assert_called_with([
        'sudo', 'umount', '/source_dir'
    ])

  def testInvalidTarget(self):
    with self.assertRaises(KeyError):
      overlay.Overlay(
          target='unknown',
          source_dir='/source_dir')


if __name__ == '__main__':
  unittest.main()
