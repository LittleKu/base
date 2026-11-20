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
    if cache_root:
        return Path(cache_root) / "chromium.googlesource.com-chromium-src"
    return None


def read_git_config(git, key):
    result = git("config", "--get", key, capture_output=True, text=True, check=False)
    if result.returncode == 1:
        return None
    result.check_returncode()
    return result.stdout.strip()


def update_shared_cache(cache_git, revision, present):
    # A shared depot_tools cache must also serve full Chromium checkouts.
    # Upgrade caches created by older versions before allowing offline reuse.
    partial_keys = ("remote.origin.promisor", "remote.origin.partialclonefilter",
                    "extensions.partialclone")
    partial = {key: read_git_config(cache_git, key) for key in partial_keys}
    shallow = cache_git("rev-parse", "--is-shallow-repository",
                        capture_output=True, text=True).stdout.strip() == "true"
    complete = read_git_config(cache_git, "base.fullCache") == "true"
    if complete and present and not shallow and not any(partial.values()):
        return

    cache_git("config", "base.fullCache", "false")
    options = ["--no-filter", "--tags", "--no-prune", "--no-prune-tags",
               "--no-write-fetch-head", "--recurse-submodules=no"]
    if shallow:
        options.append("--unshallow")
    if any(partial.values()):
        # Normal negotiation can skip blobs promised by an earlier partial fetch.
        options.append("--refetch")
    cache_git("fetch", *options, "origin", "+refs/*:refs/*",
              revision + ":refs/chromium-base/" + revision)
    if cache_git("rev-parse", "--is-shallow-repository", capture_output=True,
                 text=True).stdout.strip() != "false":
        raise RuntimeError("The shared Chromium cache still has shallow history")
    # Also fill objects referenced by older local pins that the current remote
    # refs may no longer reach. Do not declare a partial cache complete on failure.
    fetch_missing_objects(cache_git, "--all", filtered=False)
    for key, value in partial.items():
        if value is not None:
            cache_git("config", "--unset-all", key)
    cache_git("config", "base.fullCache", "true")


def fetch_missing_objects(cache_git, revision, filtered=True):
    # Local caches need only the projected source; shared caches need every
    # object reachable from their refs, including full history and Blink.
    fetched = set()
    while True:
        objects = cache_git("rev-list", "--objects", "--missing=print", "--quiet",
                            revision, capture_output=True,
                            env=dict(os.environ, GIT_NO_LAZY_FETCH="1")).stdout
        missing = {line[1:] for line in objects.splitlines()
                   if line.startswith(b"?")}
        if not missing:
            return
        if missing & fetched:
            raise RuntimeError("Chromium cache still lacks requested source objects")
        # Match Git's lazy-fetch options: normal negotiation can treat a
        # promised blob as already reachable and omit it from the response.
        cache_git("-c", "fetch.negotiationAlgorithm=noop", "fetch",
                  "--no-tags" if filtered else "--tags", "--no-write-fetch-head",
                  "--no-prune", "--no-prune-tags", "--recurse-submodules=no",
                  "--filter=blob:none" if filtered else "--no-filter", "--stdin", "origin",
                  input=b"\n".join(sorted(missing)) + b"\n")
        fetched.update(missing)


def sync_source(root, revision):
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Chromium revision must be a full lowercase commit SHA")
    root = Path(root).resolve()
    managed_paths = (*SOURCE_DIRS, "chrome/VERSION")
    # Each project needs its own HEAD/index for the imported source snapshot.
    # Source objects and projected trees use the shared cache when configured.
    snapshot_dir = root / ".chromium.git"
    cache = find_git_cache()
    git_dir = cache.resolve() if cache else snapshot_dir
    if not snapshot_dir.exists():
        existing = [name for name in managed_paths if (root / name).exists()]
        if existing:
            raise RuntimeError("Use a fresh checkout; existing source directories: " +
                               ", ".join(existing))
        subprocess.run(["git", "init", "--bare", str(snapshot_dir)], check=True)

    command = ["git", "-c", "core.longpaths=true", "--git-dir=" + str(snapshot_dir),
               "--work-tree=" + str(root)]

    def git(*args, **kwargs):
        return subprocess.run(command + list(args), check=True, **kwargs)

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

    new_cache = not git_dir.exists()
    if new_cache:
        subprocess.run(["git", "init", "--bare", str(git_dir)], check=True)
    cache_command = ["git", "-c", "core.longpaths=true",
                     "--git-dir=" + str(git_dir)]

    def cache_git(*args, check=True, **kwargs):
        return subprocess.run(cache_command + list(args), check=check, **kwargs)

    if git_dir != snapshot_dir:
        cache_git("config", "remote.origin.url", CHROMIUM_URL)

    present = subprocess.run(
        cache_command + ["cat-file", "-e", revision + "^{commit}"],
        capture_output=True, env=dict(os.environ, GIT_NO_LAZY_FETCH="1"))
    if git_dir != snapshot_dir:
        update_shared_cache(cache_git, revision, present.returncode == 0)
    elif present.returncode:
        cache_git("fetch", "--depth=1", "--filter=blob:none", "--no-tags",
                  "--no-write-fetch-head", "--recurse-submodules=no", "origin",
                  revision + ":refs/chromium-base/" + revision)
    # The project's snapshot cannot keep borrowed objects alive during cache GC.
    cache_git("update-ref", "refs/chromium-base/" + revision, revision)

    if git_dir != snapshot_dir:
        alternates = snapshot_dir / "objects" / "info" / "alternates"
        paths = (alternates.read_text(encoding="utf-8").splitlines()
                 if alternates.exists() else [])
        objects = (git_dir / "objects").as_posix()
        if objects not in paths:
            # Keep older caches visible when changing GIT_CACHE_PATH so existing
            # snapshots and their local-change checks can still read old objects.
            alternates.write_text("\n".join([*paths, objects]) + "\n",
                                  encoding="utf-8", newline="\n")

    def make_tree(entries):
        return cache_git("mktree", "-z", "--missing", input=entries,
                         capture_output=True).stdout.strip()

    # Blink is unrelated to standalone base and dominates the source checkout.
    third_party = cache_git("ls-tree", "-z", revision + ":third_party",
                            capture_output=True).stdout
    third_party = b"".join(entry + b"\0" for entry in third_party.split(b"\0")
                          if entry and entry.split(b"\t", 1)[1] != b"blink")
    third_party_tree = make_tree(third_party)
    chrome_version = cache_git("ls-tree", "-z", revision + ":chrome", "--", "VERSION",
                               capture_output=True).stdout
    chrome_tree = make_tree(chrome_version)
    # Track only imported directories so upstream root files cannot touch ours.
    directories = [name for name in SOURCE_DIRS if name != "third_party"]
    entries = cache_git("ls-tree", "-z", revision, "--", *directories,
                        capture_output=True).stdout
    entries += b"040000 tree " + third_party_tree + b"\tthird_party\0"
    entries += b"040000 tree " + chrome_tree + b"\tchrome\0"
    tree = make_tree(entries).decode("ascii")
    # These projected trees are absent from the upstream commit. Keep them
    # reachable in the cache even though snapshot commits belong to projects.
    cache_git("update-ref", "refs/chromium-base/trees/" + tree, tree)
    if git_dir == snapshot_dir:
        fetch_missing_objects(cache_git, tree)
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
