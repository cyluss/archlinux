#!/usr/bin/env python3
"""Restore home directory from restic S3 backup.

Usage:
    From archiso:   python3 /mnt/usb/archlinux/restore.py /mnt
    After install:  python3 restore.py ~
    List snapshots: python3 restore.py --list

Expects USB at /mnt/usb or script directory with secrets/.
"""

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path

BUCKET = "hgkang-backup"
REGION = "ap-northeast-2"
HOSTNAME = os.uname().nodename


def run(cmd, check=True):
    print(f"  -> {cmd}")
    return subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)


def find_secrets():
    candidates = [
        Path(__file__).resolve().parent / "secrets",
        Path("/mnt/usb/secrets"),
        Path("/mnt/archlinux/secrets"),
    ]
    for d in candidates:
        if (d / f"restic-password-{HOSTNAME}").exists():
            return d
    for d in candidates:
        for f in d.glob("restic-password-*"):
            return d
    return None


def load_aws_credentials(secrets_dir):
    for name in ["rootkey.csv", "../rootkey.csv"]:
        p = secrets_dir / name
        if p.exists():
            with open(p) as f:
                reader = csv.reader(f)
                next(reader)
                row = next(reader)
                return row[0].strip(), row[1].strip()
    parent = secrets_dir.parent
    p = parent / "rootkey.csv"
    if p.exists():
        with open(p) as f:
            reader = csv.reader(f)
            next(reader)
            row = next(reader)
            return row[0].strip(), row[1].strip()
    print("error: rootkey.csv not found")
    sys.exit(1)


def find_password_file(secrets_dir):
    exact = secrets_dir / f"restic-password-{HOSTNAME}"
    if exact.exists():
        return exact
    for f in sorted(secrets_dir.glob("restic-password-*")):
        return f
    print("error: restic password file not found")
    sys.exit(1)


def restic_env(secrets_dir):
    key_id, secret = load_aws_credentials(secrets_dir)
    password_file = find_password_file(secrets_dir)
    prefix = HOSTNAME
    env = os.environ.copy()
    env["AWS_ACCESS_KEY_ID"] = key_id
    env["AWS_SECRET_ACCESS_KEY"] = secret
    env["RESTIC_REPOSITORY"] = f"s3:s3.{REGION}.amazonaws.com/{BUCKET}/{prefix}"
    env["RESTIC_PASSWORD_FILE"] = str(password_file)
    return env


def ensure_restic():
    if subprocess.run("which restic", shell=True, capture_output=True).returncode == 0:
        return
    print("installing restic...")
    run("pacman -Sy --noconfirm restic")


def list_snapshots(env):
    result = subprocess.run(
        ["restic", "snapshots"],
        env=env, capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)


def restore(target, snapshot, env):
    target = Path(target).resolve()
    target.mkdir(parents=True, exist_ok=True)
    print(f"\nrestoring {snapshot} -> {target}")
    cmd = ["restic", "restore", snapshot, "--target", str(target)]
    result = subprocess.run(cmd, env=env)
    if result.returncode == 0:
        print(f"\n=== restore complete -> {target} ===")
    else:
        print("\n=== restore failed ===", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Restore from restic S3 backup")
    parser.add_argument("target", nargs="?", default=None,
                        help="restore target directory (e.g. /mnt or ~)")
    parser.add_argument("--list", action="store_true",
                        help="list available snapshots")
    parser.add_argument("--snapshot", default="latest",
                        help="snapshot ID to restore (default: latest)")
    args = parser.parse_args()

    secrets_dir = find_secrets()
    if not secrets_dir:
        print("error: secrets directory not found")
        print("  expected: secrets/restic-password-<hostname> + rootkey.csv")
        sys.exit(1)
    print(f"secrets: {secrets_dir}")

    ensure_restic()
    env = restic_env(secrets_dir)

    if args.list:
        list_snapshots(env)
        return

    if not args.target:
        parser.error("target directory required (or use --list)")

    list_snapshots(env)
    restore(args.target, args.snapshot, env)


if __name__ == "__main__":
    main()
