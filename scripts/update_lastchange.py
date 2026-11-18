#!/usr/bin/env python3
"""Generate build metadata from the pinned Chromium commit."""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def update_lastchange(root, revision):
    root = Path(root).resolve()
    timestamp = subprocess.check_output([
        "git", "--git-dir=" + str(root / ".chromium.git"),
        "show", "-s", "--format=%ct", revision,
    ], text=True).strip()
    environment = dict(os.environ, BASE_COMMIT_HASH=revision,
                       BASE_COMMIT_SUBMISSION_MS=str(int(timestamp) * 1000))
    for arguments in (("-o", "build/util/LASTCHANGE"),
                      ("--minibranch-out", "build/util/MINIBRANCH")):
        subprocess.run([sys.executable, "build/util/lastchange.py", *arguments],
                       cwd=root, env=environment, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("revision")
    arguments = parser.parse_args()
    update_lastchange(Path(__file__).resolve().parents[1], arguments.revision)
