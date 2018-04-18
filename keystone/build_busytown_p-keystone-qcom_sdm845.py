"""Builds p-keystone-qcom sdm845 on an Busytown build host
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import nsjail
import os

def build(nsjail_bin, chroot, dist_dir, build_id, max_cpus):
  """Build inside NsJail sandbox.

  Args:
    nsjail_bin: A string with the path to the nsjail binary.
    chroot: A string with the path to the chroot.
    dist_dir: A string with the path to the dist directory.
    build_id: A string with the build identifier.
    max_cpus: An integer with maximum number of CPUs.
  """
  source_dir=os.getcwd()
  command = ['/src/development/keystone/build_keystone.sh', 'sdm845-userdebug']
  nsjail.run(
      nsjail_bin=nsjail_bin,
      chroot=chroot,
      source_dir=source_dir,
      command=command,
      dist_dir=dist_dir,
      build_id=build_id,
      max_cpus=max_cpus)

def main():
  # Use the top level module docstring for the help description
  parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument(
      '--nsjail_bin',
      required=True,
      default='/bin/nsjail',
      help='Path to NsJail binary.')
  parser.add_argument(
      '--chroot',
      required=True,
      help='Required. Path to the chroot to be used for building the Android'
      'platform. This will be mounted as the root filesystem in the'
      'NsJail sanbox.')
  parser.add_argument(
      '--dist_dir',
      required=True,
      help='Path to the Android dist directory. This is where'
      'Android platform release artifacts will be written.'
      'If unset then the Android platform default will be used.')
  parser.add_argument(
      '--build_id',
      required=True,
      help='Build identifier what will label the Android platform'
      'release artifacts.')
  parser.add_argument(
      '--max_cpus',
      required=True,
      type=int,
      help='Limit of concurrent CPU cores that the NsJail sanbox'
      'can use. Defaults to unlimited.')
  args = parser.parse_args()
  build(
      chroot=args.chroot,
      nsjail_bin=args.nsjail_bin,
      dist_dir=args.dist_dir,
      build_id=args.build_id,
      max_cpus=args.max_cpus)


if __name__ == '__main__':
  main()
