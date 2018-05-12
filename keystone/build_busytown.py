"""Builds an Android target on a Busytown build host.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os
import nsjail


def build(android_target, nsjail_bin, chroot, dist_dir, build_id, max_cpus):
  """Builds an Android target on a Busytown build host.

  Args:
    android_target: A string with the name of the android target to build.
    nsjail_bin: A string with the path to the nsjail binary.
    chroot: A string with the path to the chroot of the
      NsJail sandbox.
    dist_dir: A string with the path to the Android dist directory.
    build_id: A string with the Android build identifier.
    max_cpus: An integer with maximum number of CPUs.
  """
  # All busytown builds run with the root of the
  # Android source tree as the current directory.
  source_dir = os.getcwd()
  command = [
      '/src/development/keystone/build_keystone.sh',
      android_target + '-userdebug',
      '/src',
      'make', '-j', 'droid', 'showcommands', 'dist', 'platform_tests'
  ]
  nsjail.run(
      nsjail_bin=nsjail_bin,
      chroot=chroot,
      source_dir=source_dir,
      command=command,
      android_target=android_target,
      dist_dir=dist_dir,
      build_id=build_id,
      max_cpus=max_cpus)


def parse_args():
  """Parses command line arguments.

  Returns:
    A dict of all the arguments parsed.
  """
  # Use the top level module docstring for the help description
  parser = argparse.ArgumentParser(
      description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument(
      '--nsjail_bin',
      required=True,
      default='/bin/nsjail',
      help='Path to NsJail binary.')
  parser.add_argument(
      '--chroot',
      required=True,
      help='Path to the chroot to be used for building the Android '
      'platform. This will be mounted as the root filesystem in the '
      'NsJail sanbox.')
  parser.add_argument(
      '--dist_dir',
      required=True,
      help='Path to the Android dist directory. This is where '
      'Android platform release artifacts will be written.'
      'If unset then the Android platform default will be used.')
  parser.add_argument(
      '--build_id',
      required=True,
      help='Build identifier what will label the Android platform '
      'release artifacts.')
  parser.add_argument(
      '--max_cpus',
      required=True,
      type=int,
      help='Limit of concurrent CPU cores that the NsJail sanbox '
      'can use. Defaults to unlimited.')
  # Convert the Namespace object to a dict
  return vars(parser.parse_args())

def build_target(android_target):
  args = parse_args()
  build(android_target=android_target, **args)
