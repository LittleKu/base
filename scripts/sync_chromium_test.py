import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sync_chromium
import update_lastchange


class SyncSourceTest(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ, {
            "GIT_CACHE_PATH": "",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
        })
        environment.start()
        self.addCleanup(environment.stop)

    def test_rejects_depot_tools_drift(self):
        with (patch.object(sync_chromium.shutil, "which", return_value="/tools/gclient"),
              patch.object(subprocess, "check_output", return_value="a" * 40)):
            with self.assertRaises(RuntimeError):
                sync_chromium.check_depot_tools()

    def test_checkout_upgrade_and_local_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            upstream = directory / "upstream"
            upstream.mkdir()

            def git(*args):
                return subprocess.check_output(
                    ["git", "-C", str(upstream), *args], text=True).strip()

            git("init")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.invalid")
            for name in (".gn", "BUILD.gn", "DEPS"):
                (upstream / name).write_text("upstream", encoding="utf-8")
            (upstream / "base").mkdir()
            (upstream / "base" / "source.cc").write_text("first", encoding="utf-8")
            (upstream / "chrome").mkdir()
            (upstream / "chrome" / "VERSION").write_text("first", encoding="utf-8")
            (upstream / "chrome" / "browser.cc").write_text("omit", encoding="utf-8")
            (upstream / "build" / "config").mkdir(parents=True)
            (upstream / "build" / "config" / "BUILD.gn").write_text("source", encoding="utf-8")
            for name in ("blink", "abseil-cpp", "blinkish"):
                (upstream / "third_party" / name).mkdir(parents=True)
                (upstream / "third_party" / name / "source.cc").write_text(
                    name, encoding="utf-8")
            git("add", ".")
            with patch.dict(os.environ, {"GIT_COMMITTER_DATE": "2026-11-10T01:02:03Z"}):
                git("commit", "-m", "first")
            first = git("rev-parse", "HEAD")
            (upstream / "base" / "source.cc").write_text("second", encoding="utf-8")
            (upstream / "chrome" / "VERSION").write_text("second", encoding="utf-8")
            (upstream / "base" / "added.cc").write_text("upstream", encoding="utf-8")
            (upstream / ".gn").write_text("changed upstream", encoding="utf-8")
            git("add", ".")
            git("commit", "-m", "second")
            second = git("rev-parse", "HEAD")

            project = directory / "project"
            project.mkdir()
            subprocess.run(["git", "init", str(project)], check=True,
                           capture_output=True)
            for name in (".gn", "BUILD.gn", "DEPS"):
                (project / name).write_text("project", encoding="utf-8")
            (project / ".gitignore").write_text("/base/\n", encoding="utf-8")
            (project / "chrome").mkdir()
            (project / "chrome" / "local.txt").write_text("local", encoding="utf-8")

            with patch.object(sync_chromium, "CHROMIUM_URL", upstream.as_uri()):
                for revision, content in ((first, "first"), (first, "first"),
                                          (second, "second")):
                    if revision == second:
                        conflict = project / "base" / "added.cc"
                        conflict.write_text("local untracked", encoding="utf-8")
                        with self.assertRaises(subprocess.CalledProcessError):
                            sync_chromium.sync_source(project, second)
                        self.assertEqual(conflict.read_text(), "local untracked")
                        conflict.unlink()
                    sync_chromium.sync_source(project, revision)
                    generated = project / "build" / "config" / "gclient_args.gni"
                    if generated.exists():
                        self.assertEqual(generated.read_text(), "generated")
                    else:
                        generated.write_text("generated", encoding="utf-8")
                    self.assertEqual((project / "base" / "source.cc").read_text(),
                                     content)
                    self.assertEqual((project / "chrome" / "VERSION").read_text(), content)
                    self.assertEqual((project / "chrome" / "local.txt").read_text(), "local")
                    self.assertFalse((project / "chrome" / "browser.cc").exists())
                    self.assertFalse((project / "third_party" / "blink").exists())
                    for name in ("abseil-cpp", "blinkish"):
                        self.assertEqual(
                            (project / "third_party" / name / "source.cc").read_text(), name)
                    for name in (".gn", "BUILD.gn", "DEPS"):
                        self.assertEqual((project / name).read_text(), "project")
                # Simulate a successful older projection of the same revision.
                source_git = ["git", "--git-dir=" + str(project / ".chromium.git"),
                              "--work-tree=" + str(project)]
                subprocess.run(source_git + ["rm", "chrome/VERSION"], check=True,
                               capture_output=True)
                subprocess.run(source_git + ["commit", "-m", "Older source projection"],
                               check=True, capture_output=True)
                version_file = project / "chrome" / "VERSION"
                version_file.write_text("local untracked", encoding="utf-8")
                with self.assertRaises(subprocess.CalledProcessError):
                    sync_chromium.sync_source(project, second)
                self.assertEqual(version_file.read_text(), "local untracked")
                version_file.unlink()
                sync_chromium.sync_source(project, second)
                self.assertEqual(version_file.read_text(), "second")
                version_file.write_text("local tracked", encoding="utf-8")
                with self.assertRaises(subprocess.CalledProcessError):
                    sync_chromium.sync_source(project, second)
                version_file.write_text("second", encoding="utf-8")
                (project / "base" / "source.cc").write_text("local", encoding="utf-8")
                with self.assertRaises(subprocess.CalledProcessError):
                    sync_chromium.sync_source(project, first)
                self.assertEqual((project / "base" / "source.cc").read_text(), "local")
                marked = subprocess.check_output([
                    "git", "--git-dir=" + str(project / ".chromium.git"),
                    "config", "base.chromiumRevision"], text=True).strip()
                self.assertEqual(marked, second)

            (project / "base" / "source.cc").write_text("second", encoding="utf-8")
            with patch.object(sync_chromium, "CHROMIUM_URL", "file:///does-not-exist"):
                sync_chromium.sync_source(project, second)
            with patch.object(update_lastchange, "subprocess") as process:
                process.check_output.side_effect = subprocess.check_output
                update_lastchange.update_lastchange(project, first)
            self.assertEqual(process.run.call_count, 2)
            for call in process.run.call_args_list:
                self.assertEqual(call.kwargs["env"]["BASE_COMMIT_HASH"], first)
                self.assertEqual(call.kwargs["env"]["BASE_COMMIT_SUBMISSION_MS"],
                                 "1794272523000")

    def test_rejects_existing_unmanaged_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "base").mkdir()
            with self.assertRaises(RuntimeError):
                sync_chromium.sync_source(root, "a" * 40)
            self.assertFalse((root / ".chromium.git").exists())


class LocalCacheTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.upstream = self.directory / "upstream"
        self.cache_root = self.directory / "old cache root"
        self.cache = self.cache_root / "chromium.googlesource.com-chromium-src"
        environment = patch.dict(os.environ, {
            "GIT_CACHE_PATH": str(self.cache_root),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
        })
        environment.start()
        self.addCleanup(environment.stop)
        remote = patch.object(sync_chromium, "CHROMIUM_URL", self.upstream.as_uri())
        remote.start()
        self.addCleanup(remote.stop)

        self.upstream.mkdir()
        self.git("-C", self.upstream, "init")
        self.git("-C", self.upstream, "config", "user.name", "Test")
        self.git("-C", self.upstream, "config", "user.email", "test@example.invalid")
        self.git("-C", self.upstream, "config", "uploadpack.allowFilter", "true")
        self.git("-C", self.upstream, "config", "uploadpack.allowAnySHA1InWant", "true")
        for name, content in {
            ".gn": "upstream root file",
            "base/source.cc": "first base",
            "chrome/VERSION": "first version",
            "chrome/browser.cc": "excluded browser",
            "third_party/README.md": "imported third party metadata",
            "third_party/dependency/source.cc": "imported dependency",
            "third_party/blink/source.cc": "excluded blink",
        }.items():
            file = self.upstream / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content, encoding="utf-8")
        self.first = self.commit("first")
        (self.upstream / "base" / "source.cc").write_text("second base", encoding="utf-8")
        (self.upstream / "chrome" / "VERSION").write_text("second version", encoding="utf-8")
        self.second = self.commit("second")

    @staticmethod
    def git(*args):
        return subprocess.check_output(
            ["git", *(str(arg) for arg in args)], text=True).strip()

    def commit(self, message):
        self.git("-C", self.upstream, "add", ".")
        self.git("-C", self.upstream, "commit", "-m", message)
        return self.git("-C", self.upstream, "rev-parse", "HEAD")

    def project(self, name):
        project = self.directory / name
        project.mkdir()
        return project

    @staticmethod
    def has_object(git_dir, object_id):
        return subprocess.run(
            ["git", "--git-dir=" + str(git_dir), "cat-file", "-e", object_id],
            capture_output=True,
            env=dict(os.environ, GIT_NO_LAZY_FETCH="1")).returncode == 0

    @staticmethod
    def repository_files(repository):
        return {file.relative_to(repository): file.read_bytes()
                for file in repository.rglob("*") if file.is_file()}

    def assert_complete_revision(self, repository, revision):
        with patch.dict(os.environ, {"GIT_NO_LAZY_FETCH": "1"}):
            objects = self.git("--git-dir=" + str(repository), "rev-list", "--objects",
                               "--missing=print", "--no-object-names", revision + "^{tree}")
        self.assertFalse(any(line.startswith("?") for line in objects.splitlines()))
        for file in ("base/source.cc", "chrome/VERSION", ".gn", "chrome/browser.cc",
                     "third_party/blink/source.cc"):
            blob = self.git("-C", self.upstream, "rev-parse", revision + ":" + file)
            self.assertTrue(self.has_object(repository, blob), file)

    def create_legacy_snapshot(self, project, revision, source_git):
        snapshot = project / ".chromium.git"
        if not snapshot.exists():
            self.git("init", "--bare", snapshot)
        if source_git != snapshot:
            (snapshot / "objects" / "info" / "alternates").write_text(
                (source_git / "objects").as_posix() + "\n", encoding="utf-8", newline="\n")
        command = ["git", "--git-dir=" + str(snapshot), "--work-tree=" + str(project)]
        source_command = ["git", "--git-dir=" + str(source_git)]
        for key, value in (("user.name", "Test"), ("user.email", "test@example.invalid"),
                           ("remote.origin.url", self.upstream.as_uri()),
                           ("remote.origin.promisor", "true"),
                           ("remote.origin.partialclonefilter", "blob:none")):
            self.git(*command[1:], "config", key, value)

        def entries(*args):
            return subprocess.check_output(source_command + ["ls-tree", "-z", *args])

        def tree(data):
            return subprocess.check_output(
                source_command + ["mktree", "-z", "--missing"], input=data).strip()

        third_party = b"".join(
            entry + b"\0" for entry in entries(revision + ":third_party").split(b"\0")
            if entry and entry.split(b"\t", 1)[1] != b"blink")
        third_party_tree = tree(third_party)
        chrome_tree = tree(entries(revision + ":chrome", "--", "VERSION"))
        root_entries = entries(revision, "--", "base")
        root_entries += b"040000 tree " + third_party_tree + b"\tthird_party\0"
        root_entries += b"040000 tree " + chrome_tree + b"\tchrome\0"
        snapshot_tree = tree(root_entries).decode("ascii")
        commit = self.git(*command[1:], "commit-tree", snapshot_tree, "-m", "Legacy snapshot")
        self.git(*command[1:], "checkout", "--detach", commit)
        self.git(*command[1:], "config", "base.chromiumRevision", revision)
        return commit

    def test_ignores_external_caches_and_fetches_complete_shallow_revision(self):
        self.git("-C", self.upstream, "checkout", "-b", "extra-branch", self.first)
        (self.upstream / "branch-only.txt").write_text("other branch", encoding="utf-8")
        extra_commit = self.commit("other branch")
        self.git("-C", self.upstream, "checkout", "--detach", self.second)
        self.git("clone", "--mirror", self.upstream.as_uri(), self.cache)
        original_cache = self.repository_files(self.cache)
        global_config = self.directory / "gitconfig"
        self.git("config", "--file", global_config, "cache.cachepath", self.cache_root)

        for index, cache_environment in enumerate((str(self.cache_root), "")):
            with self.subTest(cache_environment=cache_environment):
                project = self.project("project-" + str(index))
                with patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(global_config),
                                             "GIT_CACHE_PATH": cache_environment}):
                    sync_chromium.sync_source(project, self.second)
                local = project / ".chromium.git"
                self.assert_complete_revision(local, self.second)
                self.assertFalse(self.has_object(local, self.first))
                self.assertFalse(self.has_object(local, extra_commit))
                self.assertEqual(self.git("--git-dir=" + str(local), "rev-parse",
                                          "--is-shallow-repository"), "true")
                self.assertFalse((local / "objects" / "info" / "alternates").exists())
                self.assertEqual((project / "base" / "source.cc").read_text(), "second base")
                self.assertFalse((project / "third_party" / "blink").exists())
                self.assertFalse((project / "chrome" / "browser.cc").exists())
                self.assertFalse((project / ".gn").exists())
                self.assertEqual(self.repository_files(self.cache), original_cache)

    def test_migrates_existing_partial_local_cache(self):
        project = self.project("project")
        local = project / ".chromium.git"
        self.git("clone", "--bare", "--depth=1", "--filter=blob:none",
                 "--single-branch", "--no-tags", self.upstream.as_uri(), local)
        self.create_legacy_snapshot(project, self.second, local)
        blink_blob = self.git("-C", self.upstream, "rev-parse",
                              self.second + ":third_party/blink/source.cc")
        self.assertFalse(self.has_object(local, blink_blob))
        sync_chromium.sync_source(project, self.second)
        self.assert_complete_revision(local, self.second)
        self.assertFalse(self.has_object(local, self.first))
        self.assertEqual((project / "base" / "source.cc").read_text(), "second base")
        self.assertFalse((project / "third_party" / "blink").exists())
        with patch.object(sync_chromium, "CHROMIUM_URL", "file:///does-not-exist"):
            sync_chromium.sync_source(project, self.second)
        self.assertFalse(self.cache_root.exists())

    def test_partial_migration_fills_objects_for_older_revision_pins(self):
        (self.upstream / ".gn").write_text("new upstream root file", encoding="utf-8")
        target = self.commit("new root file")
        project = self.project("project")
        local = project / ".chromium.git"
        self.git("init", "--bare", local)
        for key, value in (("remote.origin.url", self.upstream.as_uri()),
                           ("remote.origin.promisor", "true"),
                           ("remote.origin.partialclonefilter", "blob:none")):
            self.git("--git-dir=" + str(local), "config", key, value)
        for revision in (self.first, target):
            self.git("--git-dir=" + str(local), "fetch", "--depth=1", "--filter=blob:none",
                     "origin", revision + ":refs/chromium-base/" + revision)
            self.create_legacy_snapshot(project, revision, local)

        old_root_blob = self.git("-C", self.upstream, "rev-parse", self.first + ":.gn")
        self.assertFalse(self.has_object(local, old_root_blob))
        sync_chromium.sync_source(project, target)
        self.assert_complete_revision(local, self.first)
        self.assert_complete_revision(local, target)
        with patch.dict(os.environ, {"GIT_NO_LAZY_FETCH": "1"}):
            objects = self.git("--git-dir=" + str(local), "rev-list", "--objects",
                               "--missing=print", "--no-object-names", "--all", "--reflog")
            self.assertFalse(any(line.startswith("?") for line in objects.splitlines()))
            self.assertEqual(self.git("--git-dir=" + str(local), "show", self.first + ":.gn"),
                             "upstream root file")
        for key in ("remote.origin.promisor", "remote.origin.partialclonefilter",
                    "extensions.partialclone"):
            config = subprocess.run(
                ["git", "--git-dir=" + str(local), "config", "--local", "--get", key],
                capture_output=True)
            self.assertEqual(config.returncode, 1, key)
        self.assertEqual(self.git("--git-dir=" + str(local), "rev-parse",
                                  "--is-shallow-repository"), "true")

    def test_migrates_borrowed_snapshot_without_retaining_cache_dependency(self):
        self.git("clone", "--mirror", self.upstream.as_uri(), self.cache)
        project = self.project("project")
        local = project / ".chromium.git"
        snapshot = self.create_legacy_snapshot(project, self.first, self.cache)
        original_cache = self.repository_files(self.cache)
        source_file = project / "base" / "source.cc"
        source_file.write_text("local change", encoding="utf-8")
        with self.assertRaises(subprocess.CalledProcessError):
            sync_chromium.sync_source(project, self.second)
        self.assertTrue((local / "objects" / "info" / "alternates").exists())
        self.assertEqual(source_file.read_text(), "local change")
        source_file.write_text("first base", encoding="utf-8")
        sync_chromium.sync_source(project, self.second)
        self.assertFalse((local / "objects" / "info" / "alternates").exists())
        self.assertEqual(self.repository_files(self.cache), original_cache)

        moved_cache = self.directory / "unavailable-cache"
        self.assertTrue(self.cache.resolve().is_relative_to(self.directory.resolve()))
        self.assertTrue(moved_cache.resolve().is_relative_to(self.directory.resolve()))
        self.cache.rename(moved_cache)
        with patch.dict(os.environ, {"GIT_NO_LAZY_FETCH": "1"}):
            self.assertEqual(self.git("--git-dir=" + str(local), "show",
                                      snapshot + ":base/source.cc"), "first base")
            self.assertEqual(self.git("--git-dir=" + str(local), "show",
                                      "HEAD:chrome/VERSION"), "second version")
        self.assert_complete_revision(local, self.second)
        with patch.object(sync_chromium, "CHROMIUM_URL", "file:///does-not-exist"):
            sync_chromium.sync_source(project, self.second)


if __name__ == "__main__":
    unittest.main()
