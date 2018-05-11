"""Runs a command inside an NsJail sandbox for building Android.

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
from overlay import Overlay


def create_user(user_id, group_id):
  name = 'android-build'
  subprocess.check_call([
      'groupadd', name,
      '--gid', str(group_id)
  ])
  subprocess.check_call([
      'useradd',
      '--gid', name,
      '--groups', 'sudo',
      '--uid', str(user_id),
      '--create-home', name
  ])


def run(nsjail_bin,
        chroot,
        source_dir,
        command,
        android_target,
        dist_dir,
        build_id,
        max_cpus,
        user_id=None,
        group_id=None):
  """Run inside an NsJail sandbox.

  Args:
    nsjail_bin: A string with the path to the nsjail binary.
    chroot: A string with the path to the chroot.
    source_dir: A string with the path to the Android platform source.
    command: A list of strings with the command to run.
    android_target: A string with the name of the target to be prepared
      inside the container.
    dist_dir: A string with the path to the dist directory.
    build_id: A string with the build identifier.
    max_cpus: An integer with maximum number of CPUs.
    user_id: An integer with the user ID to run the build process under.
    group_id: An integer with the group ID to run the build process under.
  """
  if user_id and group_id:
    create_user(user_id, group_id)
    os.setgid(group_id)
    os.setuid(user_id)

  overlay = None
  # Apply the overlay for the selected Android target
  # to the source directory if overlays are present
  if os.path.exists(os.path.join(source_dir, 'overlays')):
    overlay = Overlay(android_target, source_dir)

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
    nsjail_command.extend(['--env', 'BUILD_NUMBER=%s' % build_id])
  if max_cpus:
    nsjail_command.append('--max_cpus=%i' % max_cpus)

  nsjail_command.append('--')
  nsjail_command.extend(command)

  print('NsJail command:')
  print(' '.join(nsjail_command))
  subprocess.call(nsjail_command)

  # Strip out overlay
  del overlay


def main():
  # Use the top level module docstring for the help description
  parser = argparse.ArgumentParser(
      description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument(
      '--nsjail_bin', default='/bin/nsjail', help='Path to NsJail binary.')
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
      '--android_target',
      required=True,
      help='Android target selected for building')
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
      '--user_id',
      type=int,
      help='User ID to run the build process under. Defaults to current user.')
  parser.add_argument(
      '--group_id',
      type=int,
      help='Group ID to run the build process under. Defaults to current group.'
  )
  parser.add_argument(
      '--max_cpus',
      type=int,
      help='Limit of concurrent CPU cores that the NsJail sanbox'
      'can use. Defaults to unlimited.')
  args = parser.parse_args()
  run(chroot=args.chroot,
      nsjail_bin=args.nsjail_bin,
      source_dir=args.source_dir,
      command=args.command.split(),
      android_target=args.android_target,
      dist_dir=args.dist_dir,
      build_id=args.build_id,
      user_id=args.user_id,
      group_id=args.group_id,
      max_cpus=args.max_cpus)


if __name__ == '__main__':
  main()
