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


def run_patch(file, cwd=None, patch_binary=None):
    with open(file, 'rb') as f:
        # fix windows newlines
        patch_content = f.read().replace(b'\n', b'\r\n')
        with open(cwd / (file.name + 'converted.patch'), 'wb') as f2:
            f2.write(patch_content)
        subprocess.run([patch_binary, '--quiet', '--force', '--no-backup-if-mismatch', '--version-control', 'none', '--binary', '-p1'], cwd=cwd, check=True, input=patch_content)


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
    parser.add_argument('--patch-program',
                        help='path to the patch binary',
                        required=True,
                        type=pathlib.Path)
    args = parser.parse_args()

    eprint(f"{args.output_dir=}")
    eprint(f"{args.patches=}")
    eprint(f"{args.convert_script=}")
    eprint(f"{args.sdk_path=}")
    eprint(f"{args.patch_program=}")

    if args.output_dir.exists():
        eprint("Nothing to do.")
        return
    assert all([x.exists() for x in args.patches])
    assert args.convert_script.is_file()
    assert args.sdk_path.exists() and args.sdk_path.is_dir()
    assert args.patch_program.exists()

    eprint("Copy files.")
    shutil.copytree(args.sdk_path, args.output_dir)

    eprint("Apply patches.")
    patch = partial(run_patch, patch_binary=args.patch_program, cwd=args.output_dir)
    for patch_file in args.patches:
        patch(patch_file.absolute())

    eprint("Run script.")
    for action in ['wrap', 'svc']:
        subprocess.run([
            sys.executable, args.convert_script, '-u', '-k', action, '-s',
            args.output_dir
        ], check=True)


if __name__ == '__main__':
    main()
