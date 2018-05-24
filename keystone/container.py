"""Runs a command in an Android Build container.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os
import subprocess

_IMAGE = 'android-build'


def run(container_command, android_target, docker_bin):
  """Runs a command in an Android Build container.

  Args:
    container_command: A string with the command to be executed
      inside the container.
    android_target: A string with the name of the target to be prepared
      inside the container.
    docker_bin: A string that invokes docker.

  Returns:
    A list of strings with the command executed.
  """
  docker_command = [
      docker_bin, 'run',
      '--mount', 'type=bind,source=%s,target=/src' % os.getcwd(),
      '--tty',
      '--privileged',
      '--interactive',
      _IMAGE,
      'python', '-B', '/src/development/keystone/nsjail.py',
      '--android_target', android_target,
      '--chroot', '/',
      '--source_dir', '/src',
      '--user_id', str(os.getuid()),
      '--group_id', str(os.getgid())
  ]
  docker_command.extend(['--command', container_command])

  subprocess.check_call(docker_command)

  return docker_command


def main():
  # Use the top level module docstring for the help description
  parser = argparse.ArgumentParser(
      description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument(
      '--container_command',
      default='/bin/bash',
      help='Command to be executed inside the container. '
      'Defaults to /bin/bash.')
  parser.add_argument(
      '--android_target',
      default='sdm845',
      help='Android target for building inside container. '
      'Defaults to sdm845.')
  parser.add_argument(
      '--docker_bin',
      default='docker',
      help='Binary that invokes docker. Default to \'docker\'')
  args = parser.parse_args()
  run(container_command=args.container_command,
      android_target=args.android_target,
      docker_bin=args.docker_bin)


if __name__ == '__main__':
  main()
