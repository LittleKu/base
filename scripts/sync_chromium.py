#!/usr/bin/env python3
"""Check out the pinned Chromium source directories without replacing this project."""

import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path


CHROMIUM_URL = "https://chromium.googlesource.com/chromium/src.git"
DEPOT_TOOLS_REVISION = "b86fc981b72ab966f8260f73b4eca600b3b12677"
SOURCE_DIRS = ("base", "build", "buildtools", "testing", "third_party", "tools")


def check_depot_tools():
    gclient = shutil.which("gclient")
    if not gclient:
        raise RuntimeError("Put the pinned depot_tools directory first on PATH")
    actual = subprocess.check_output(
        ["git", "-C", str(Path(gclient).resolve().parent), "rev-parse", "HEAD"],
        text=True).strip()
    if actual != DEPOT_TOOLS_REVISION:
        raise RuntimeError("Expected depot_tools " + DEPOT_TOOLS_REVISION +
                           "; active version is " + actual)


def find_git_cache():
    cache_root = os.environ.get("GIT_CACHE_PATH")
    if not cache_root:
        result = subprocess.run(["git", "config", "--path", "--get", "cache.cachepath"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            cache_root = result.stdout.strip()
    if cache_root:
        cache = Path(cache_root) / "chromium.googlesource.com-chromium-src"
        if (cache / "objects").is_dir():
            return cache
    return None


def sync_source(root, revision):
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Chromium revision must be a full lowercase commit SHA")
    root = Path(root).resolve()
    managed_paths = (*SOURCE_DIRS, "chrome/VERSION")
    git_dir = root / ".chromium.git"
    if not git_dir.exists():
        existing = [name for name in managed_paths if (root / name).exists()]
        if existing:
            raise RuntimeError("Use a fresh checkout; existing source directories: " +
                               ", ".join(existing))
        subprocess.run(["git", "init", "--bare", str(git_dir)], check=True)

    command = ["git", "-c", "core.longpaths=true", "--git-dir=" + str(git_dir),
               "--work-tree=" + str(root)]

    def git(*args, **kwargs):
        return subprocess.run(command + list(args), check=True, **kwargs)

    cache = find_git_cache()
    if cache:
        # Borrow existing depot_tools objects without changing the shared cache.
        (git_dir / "objects" / "info" / "alternates").write_text(
            (cache.resolve() / "objects").as_posix() + "\n", encoding="utf-8",
            newline="\n")
    git("config", "remote.origin.url", CHROMIUM_URL)
    git("config", "remote.origin.promisor", "true")
    git("config", "remote.origin.partialclonefilter", "blob:none")
    git("config", "user.name", "Chromium source snapshot")
    git("config", "user.email", "source-snapshot@example.invalid")

    head = subprocess.run(command + ["rev-parse", "--verify", "HEAD"],
                          capture_output=True, text=True)
    if head.returncode == 0:
        git("diff", "--exit-code", "--ignore-submodules", "--", *managed_paths)
        git("diff", "--cached", "--exit-code", "--", *managed_paths)

    present = subprocess.run(command + ["cat-file", "-e", revision + "^{commit}"],
                             capture_output=True,
                             env=dict(os.environ, GIT_NO_LAZY_FETCH="1"))
    if present.returncode:
        git("fetch", "--depth=1", "--filter=blob:none", "origin", revision)
    # Blink is unrelated to standalone base and dominates the source checkout.
    third_party = git("ls-tree", "-z", revision + ":third_party",
                      capture_output=True).stdout
    third_party = b"".join(entry + b"\0" for entry in third_party.split(b"\0")
                          if entry and entry.split(b"\t", 1)[1] != b"blink")
    third_party_tree = git("mktree", "-z", input=third_party,
                           capture_output=True).stdout.strip()
    chrome_version = git("ls-tree", "-z", revision + ":chrome", "--", "VERSION",
                         capture_output=True).stdout
    chrome_tree = git("mktree", "-z", input=chrome_version,
                      capture_output=True).stdout.strip()
    # Track only imported directories so upstream root files cannot touch ours.
    directories = [name for name in SOURCE_DIRS if name != "third_party"]
    entries = git("ls-tree", "-z", revision, "--", *directories,
                  capture_output=True).stdout
    entries += b"040000 tree " + third_party_tree + b"\tthird_party\0"
    entries += b"040000 tree " + chrome_tree + b"\tchrome\0"
    tree = git("mktree", "-z", input=entries,
               capture_output=True).stdout.decode("ascii").strip()
    if head.returncode == 0:
        current = subprocess.run(command + ["config", "base.chromiumRevision"],
                                 capture_output=True, text=True).stdout.strip()
        current_tree = git("rev-parse", "HEAD^{tree}", capture_output=True,
                           text=True).stdout.strip()
        if current == revision and current_tree == tree:
            return
    commit = git("commit-tree", tree, "-m", "Chromium " + revision,
                 capture_output=True, text=True).stdout.strip()
    git("checkout", "--no-overwrite-ignore", "--detach", commit)
    git("config", "base.chromiumRevision", revision)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("revision")
    arguments = parser.parse_args()
    check_depot_tools()
    sync_source(Path(__file__).resolve().parents[1], arguments.revision)
