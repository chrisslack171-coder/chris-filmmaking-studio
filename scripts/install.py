#!/usr/bin/env python3
"""Install the standalone skill locally; never asks for or reads API credentials."""
import argparse
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile

NAME = "chris-filmmaking-studio"


def fingerprint(path):
    return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts}


def install(parent):
    source = Path(__file__).resolve().parents[1] / "skills" / NAME
    target = Path(parent).expanduser().resolve() / NAME
    if target.exists():
        if fingerprint(source) == fingerprint(target):
            return target, "Already installed; no changes needed."
        raise RuntimeError("An existing skill differs. Back it up and remove it yourself before installing this version.")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".hf-install-", dir=target.parent) as temp:
        staged = Path(temp) / NAME
        shutil.copytree(source, staged, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        staged.rename(target)
    return target, "Installed. Select the skill in your host; restart if it does not appear."


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=Path.home() / ".codex/skills",
                        help="Parent skills directory; defaults to ~/.codex/skills")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        sys.exit("Python 3.10+ is required.")
    try:
        path, message = install(args.destination)
        print(message)
        print(path)
        print("Next: ask your assistant to use Chris Filmmaking Studio and start private onboarding.")
    except (RuntimeError, OSError) as error:
        sys.exit(str(error))
