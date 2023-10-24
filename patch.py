#!/usr/bin/env python
"""Patch the nRF5_SDK for usage with LLVM."""
import argparse
import sys
import pathlib
import shutil
import subprocess

from functools import partial


def eprint(*args):
    print(*args, file=sys.stderr)


def run_git(*args, git_dir=None, git_binary=None):
    subprocess.run([git_binary, *args], cwd=git_dir, check=True)


def main():
    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    parser.add_argument('--output-dir',
                        help='Output directory for the patches SDK',
                        required=True,
                        type=pathlib.Path)
    parser.add_argument('--patch',
                        dest='patches',
                        help='list of patches',
                        required=True,
                        action='append',
                        type=pathlib.Path)
    parser.add_argument('--convert-script',
                        help='path to convert script',
                        required=True,
                        type=pathlib.Path)
    parser.add_argument('--sdk-path',
                        help='original SDK',
                        required=True,
                        type=pathlib.Path)
    parser.add_argument('--git',
                        help='path to the git binary',
                        required=True,
                        type=pathlib.Path)
    args = parser.parse_args()

    eprint(f"{args.output_dir=}")
    eprint(f"{args.patches=}")
    eprint(f"{args.convert_script=}")
    eprint(f"{args.sdk_path=}")
    eprint(f"{args.git=}")

    if args.output_dir.exists():
        eprint("Nothing to do.")
        return
    assert all([x.exists() for x in args.patches])
    assert args.convert_script.is_file()
    assert args.sdk_path.exists() and args.sdk_path.is_dir()
    assert args.git.exists()

    eprint("Copy files.")
    shutil.copytree(args.sdk_path, args.output_dir)

    eprint("Apply patches.")
    git = partial(run_git, git_binary=args.git, git_dir=args.output_dir)
    git('init')
    git('add', '-A')
    git('commit', '-m', 'orig')
    for patch in args.patches:
        git('apply', '--reject', '--whitespace=fix', patch.absolute())
        git('add', '-A')
        git('commit', '-m', f'Applied {patch.name}')

    eprint("Run script.")
    for action in ['wrap', 'svc']:
        subprocess.run([
            sys.executable, args.convert_script, '-u', '-k', action, '-s',
            args.output_dir
        ], check=True)
        git('add', '-A')
        git('commit', '-m',
            f'Run {args.convert_script.name} with action {action}')


if __name__ == '__main__':
    main()
