#!/usr/bin/env python3
"""Check out the pinned Chromium source directories without replacing this project."""

import argparse
import os
import re
import shlex
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


def read_git_config(git, key):
    result = git("config", "--get", key, capture_output=True, text=True, check=False)
    if result.returncode == 1:
        return None
    result.check_returncode()
    return result.stdout.strip()


def sync_source(root, revision):
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Chromium revision must be a full lowercase commit SHA")

    def run_git(command, **kwargs):
        display = (subprocess.list2cmdline(command) if os.name == "nt"
                   else shlex.join(command))
        print("+ " + display, flush=True)
        return subprocess.run(command, **kwargs)

    root = Path(root).resolve()
    managed_paths = (*SOURCE_DIRS, "chrome/VERSION")
    git_dir = root / ".chromium.git"
    if not git_dir.exists():
        existing = [name for name in managed_paths if (root / name).exists()]
        if existing:
            raise RuntimeError("Use a fresh checkout; existing source directories: " +
                               ", ".join(existing))
        run_git(["git", "init", "--bare", str(git_dir)], check=True)

    command = ["git", "-c", "core.longpaths=true", "--git-dir=" + str(git_dir),
               "--work-tree=" + str(root)]

    def git(*args, check=True, **kwargs):
        return run_git(command + list(args), check=check, **kwargs)

    git("config", "remote.origin.url", CHROMIUM_URL)
    git("config", "user.name", "Chromium source snapshot")
    git("config", "user.email", "source-snapshot@example.invalid")

    head = git("rev-parse", "--verify", "HEAD", check=False,
               capture_output=True, text=True)
    if head.returncode == 0:
        git("diff", "--exit-code", "--ignore-submodules", "--", *managed_paths)
        git("diff", "--cached", "--exit-code", "--", *managed_paths)

    partial_keys = ("remote.origin.promisor", "remote.origin.partialclonefilter",
                    "extensions.partialclone")
    partial = {key: read_git_config(git, key) for key in partial_keys}
    alternates = git_dir / "objects" / "info" / "alternates"
    no_lazy_fetch = dict(os.environ, GIT_NO_LAZY_FETCH="1")
    present = git("cat-file", "-e", revision + "^{commit}", check=False,
                  capture_output=True, env=no_lazy_fetch)
    missing = b""
    if present.returncode == 0:
        missing = git("rev-list", "--objects", "--missing=print", "--quiet",
                      revision + "^{tree}", capture_output=True,
                      env=no_lazy_fetch).stdout
    if (present.returncode or missing or any(partial.values()) or
            alternates.exists() or not (git_dir / "shallow").exists()):
        # Old partial/borrowed repositories need an actual transfer even when
        # the target commit is visible, so every file of this revision is local.
        refetch = ["--refetch"] if (missing or any(partial.values()) or
                                    alternates.exists()) else []
        git("fetch", "--depth=1", "--no-filter", *refetch, "--no-tags",
            "--no-prune", "--no-prune-tags", "--no-write-fetch-head",
            "--recurse-submodules=no", "origin",
            revision + ":refs/chromium-base/" + revision)
    git("rev-list", "--objects", "--missing=error", revision + "^{tree}",
        stdout=subprocess.DEVNULL, env=no_lazy_fetch)
    git("update-ref", "refs/chromium-base/" + revision, revision)

    def finish_migration():
        if any(partial.values()):
            # Older runs may have pinned other partially fetched revisions.
            # Complete their reachable objects before removing promisor settings.
            fetched = set()
            while True:
                objects = git("rev-list", "--objects", "--all", "--reflog",
                              "--missing=print", "--quiet", capture_output=True,
                              env=no_lazy_fetch).stdout
                missing = {line[1:] for line in objects.splitlines()
                           if line.startswith(b"?")}
                if not missing:
                    break
                if missing & fetched:
                    raise RuntimeError("Chromium repository still lacks requested objects")
                git("-c", "fetch.negotiationAlgorithm=noop", "fetch", "--no-filter",
                    "--no-tags", "--no-prune", "--no-prune-tags",
                    "--no-write-fetch-head", "--recurse-submodules=no", "--stdin", "origin",
                    input=b"\n".join(sorted(missing)) + b"\n")
                fetched.update(missing)
        if alternates.exists():
            # Copy only objects reachable from this project's refs/reflog.
            # Repacking a promisor repository could copy entire shared packs.
            git("pack-objects", "--revs", "--all", "--reflog",
                "--no-use-bitmap-index", str(git_dir / "objects" / "pack" / "pack"),
                input=b"", capture_output=True)
            original = alternates.read_bytes()
            alternates.unlink()
            try:
                git("rev-list", "--objects", "--all", "--reflog", "--missing=error",
                    stdout=subprocess.DEVNULL, env=no_lazy_fetch)
            except BaseException:
                alternates.write_bytes(original)
                raise
        for key, value in partial.items():
            if value is not None:
                git("config", "--unset-all", key)

    def make_tree(entries):
        return git("mktree", "-z", input=entries, capture_output=True).stdout.strip()

    # Keep the complete revision in Git, but import only the standalone sources.
    third_party = git("ls-tree", "-z", revision + ":third_party",
                      capture_output=True).stdout
    third_party = b"".join(entry + b"\0" for entry in third_party.split(b"\0")
                          if entry and entry.split(b"\t", 1)[1] != b"blink")
    third_party_tree = make_tree(third_party)
    chrome_version = git("ls-tree", "-z", revision + ":chrome", "--", "VERSION",
                         capture_output=True).stdout
    chrome_tree = make_tree(chrome_version)
    # Track only imported directories so upstream root files cannot touch ours.
    directories = [name for name in SOURCE_DIRS if name != "third_party"]
    entries = git("ls-tree", "-z", revision, "--", *directories,
                  capture_output=True).stdout
    entries += b"040000 tree " + third_party_tree + b"\tthird_party\0"
    entries += b"040000 tree " + chrome_tree + b"\tchrome\0"
    tree = make_tree(entries).decode("ascii")
    if head.returncode == 0:
        current = git("config", "base.chromiumRevision", check=False,
                      capture_output=True, text=True).stdout.strip()
        current_tree = git("rev-parse", "HEAD^{tree}", capture_output=True,
                           text=True).stdout.strip()
        if current == revision and current_tree == tree:
            finish_migration()
            return
    commit = git("commit-tree", tree, "-m", "Chromium " + revision,
                 capture_output=True, text=True).stdout.strip()
    git("checkout", "--no-overwrite-ignore", "--detach", commit)
    git("config", "base.chromiumRevision", revision)
    finish_migration()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("revision")
    arguments = parser.parse_args()
    check_depot_tools()
    sync_source(Path(__file__).resolve().parents[1], arguments.revision)
