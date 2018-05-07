"""Runs a command inside an NsJail sandbox for building Android

NsJail creates a user namespace sandbox where
Android can be built in an isolated process.
If no command is provided then it will open
an interactive bash shell.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os
import subprocess

def run(nsjail_bin, chroot, source_dir, command, dist_dir, build_id, max_cpus):
  """Run inside an NsJail sandbox.

  Args:
    nsjail_bin: A string with the path to the nsjail binary.
    chroot: A string with the path to the chroot.
    source_dir: A string with the path to the Android platform source.
    command: A list of strings with the command to run.
    dist_dir: A string with the path to the dist directory.
    build_id: A string with the build identifier.
    max_cpus: An integer with maximum number of CPUs.
  """
  script_dir = os.path.dirname(os.path.abspath(__file__))
  config_file = os.path.join(script_dir, 'nsjail.cfg')
  nsjail_command = [
    nsjail_bin,
    '--bindmount', source_dir + ':/src',
    '--chroot', chroot,
    '--env', 'USER=android-build',
    '--config', config_file
  ]
  if dist_dir:
    nsjail_command.extend([
      '--bindmount', dist_dir + ':/dist',
      '--env', 'DIST_DIR=/dist'
    ])
  if build_id:
    nsjail_command.extend([
      '--env', 'BUILD_NUMBER=' + build_id
      ])
  if max_cpus:
    nsjail_command.append('--max_cpus=%i' % max_cpus)

  nsjail_command.append('--')
  nsjail_command.extend(command)

  print('NsJail command:')
  print(' '.join(nsjail_command))
  subprocess.check_call(nsjail_command)


def main():
  # Use the top level module docstring for the help description
  parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument(
      '--nsjail_bin',
      default='/bin/nsjail',
      help='Path to NsJail binary.')
  parser.add_argument(
      '--chroot',
      required=True,
      help='Required. Path to the chroot to be used for building the Android'
      'platform. This will be mounted as the root filesystem in the'
      'NsJail sanbox.')
  parser.add_argument(
      '--source_dir',
      default=os.getcwd(),
      help='Path to Android platform source to be mounted as /src.'
      'If no source dir is provided it is assumed it\'s already available')
  parser.add_argument(
      '--command',
      default='/bin/bash',
      help='Command to run after entering the NsJail.'
      'If not set then an interactive Bash shell will be launched')
  parser.add_argument(
      '--dist_dir',
      help='Path to the Android dist directory. This is where'
      'Android platform release artifacts will be written.'
      'If unset then the Android platform default will be used.')
  parser.add_argument(
      '--build_id',
      help='Build identifier what will label the Android platform'
      'release artifacts.')
  parser.add_argument(
      '--max_cpus',
      type=int,
      help='Limit of concurrent CPU cores that the NsJail sanbox'
      'can use. Defaults to unlimited.')
  args = parser.parse_args()
  run(
      chroot=args.chroot,
      nsjail_bin=args.nsjail_bin,
      source_dir=args.source_dir,
      command=args.command.split(),
      dist_dir=args.dist_dir,
      build_id=args.build_id,
      max_cpus=args.max_cpus)


if __name__ == '__main__':
  main()
