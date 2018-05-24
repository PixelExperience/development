"""Test overlay."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import mock
import overlay


class OverlayTest(unittest.TestCase):

  @mock.patch('overlay.os.rmdir')
  @mock.patch('overlay.tempfile.mkdtemp', return_value='/tmp/out_dir')
  @mock.patch('overlay.os.mkdir')
  @mock.patch('overlay.open')
  @mock.patch('overlay.subprocess.check_call')
  def testCreateFromValidTarget(self,
                                mock_check_call,
                                mock_open,
                                mock_mkdir,
                                mock_mkdtemp,
                                mock_rmdir):
    del mock_open, mock_mkdir, mock_mkdtemp, mock_rmdir
    o = overlay.Overlay(
        target='sdm845',
        source_dir='/source_dir')
    self.assertIsNotNone(o)
    mock_check_call.assert_has_calls([
        mock.call([
            'sudo', 'mount', '--bind', '/source_dir/out', '/tmp/out_dir'
        ]),
        mock.call([
            'sudo', 'mount',
            '--types', 'overlay',
            '--options',
            ','.join([
                'lowerdir=/source_dir/overlays/qcom-LA.UM.7.3-incoming:'
                '/source_dir',
                'upperdir=/source_dir/out/overlays/sdm845/artifacts',
                'workdir=/source_dir/out/overlays/sdm845/work'
            ]),
            'overlay',
            '/source_dir'
        ]),
        mock.call([
            'sudo', 'mount', '--bind', '/tmp/out_dir', '/source_dir/out'
        ]),
    ])

  @mock.patch('overlay.os.rmdir')
  @mock.patch('overlay.tempfile.mkdtemp', return_value='/tmp/out_dir')
  @mock.patch('overlay.os.mkdir')
  @mock.patch('overlay.open')
  @mock.patch('overlay.subprocess.check_call')
  def testDeleteFromValidTarget(self,
                                mock_check_call,
                                mock_open,
                                mock_mkdir,
                                mock_mkdtemp,
                                mock_rmdir):
    del mock_open, mock_mkdir, mock_mkdtemp, mock_rmdir
    o = overlay.Overlay(
        target='sdm845',
        source_dir='/source_dir')
    del o
    mock_check_call.assert_has_calls([
        mock.call(['sudo', 'umount', '/source_dir/out']),
        mock.call(['sudo', 'umount', '/tmp/out_dir']),
        mock.call(['sudo', 'umount', '/source_dir'])
    ])

  def testInvalidTarget(self):
    with self.assertRaises(KeyError):
      overlay.Overlay(
          target='unknown',
          source_dir='/source_dir')


if __name__ == '__main__':
  unittest.main()
