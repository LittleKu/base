import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sync_chromium
import update_lastchange


class SyncSourceTest(unittest.TestCase):
    def test_rejects_depot_tools_drift(self):
        with (patch.object(sync_chromium.shutil, "which", return_value="/tools/gclient"),
              patch.object(subprocess, "check_output", return_value="a" * 40)):
            with self.assertRaises(RuntimeError):
                sync_chromium.check_depot_tools()

    def test_cache_environment(self):
        with tempfile.TemporaryDirectory() as temporary:
            mirror = Path(temporary) / "chromium.googlesource.com-chromium-src"
            with patch.dict(os.environ, {"GIT_CACHE_PATH": temporary}):
                self.assertEqual(sync_chromium.find_git_cache(), mirror)
                self.assertFalse(mirror.exists())
                (mirror / "objects").mkdir(parents=True)
                self.assertEqual(sync_chromium.find_git_cache(), mirror)

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

            with (patch.object(sync_chromium, "CHROMIUM_URL", upstream.as_uri()),
                  patch.object(sync_chromium, "find_git_cache", return_value=None)):
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

            cached_project = directory / "cached-project"
            cached_project.mkdir()
            mirror = directory / "mirror.git"
            subprocess.run(["git", "clone", "--mirror", upstream.as_uri(), str(mirror)],
                           check=True, capture_output=True)
            with (patch.object(sync_chromium, "CHROMIUM_URL", upstream.as_uri()),
                  patch.object(sync_chromium, "find_git_cache", return_value=mirror)):
                sync_chromium.sync_source(cached_project, second)
                with patch.object(sync_chromium, "CHROMIUM_URL", "file:///does-not-exist"):
                    sync_chromium.sync_source(cached_project, second)
                self.assertEqual((cached_project / "base" / "source.cc").read_text(),
                                 "second")
                with patch.object(update_lastchange, "subprocess") as process:
                    process.check_output.side_effect = subprocess.check_output
                    update_lastchange.update_lastchange(cached_project, first)
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


class SharedCacheTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.upstream = self.directory / "upstream"
        self.cache_root = self.directory / "cache root"
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
            path = self.upstream / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.first = self.commit("first")

    @staticmethod
    def git(*args):
        return subprocess.check_output(
            ["git", *(str(arg) for arg in args)], text=True).strip()

    def commit(self, message):
        self.git("-C", self.upstream, "add", ".")
        self.git("-C", self.upstream, "commit", "-m", message)
        return self.git("-C", self.upstream, "rev-parse", "HEAD")

    def second_commit(self):
        (self.upstream / "base" / "source.cc").write_text("second base", encoding="utf-8")
        (self.upstream / "chrome" / "VERSION").write_text("second version", encoding="utf-8")
        return self.commit("second")

    def extra_refs(self):
        current_branch = self.git("-C", self.upstream, "symbolic-ref", "--short", "HEAD")
        self.git("-C", self.upstream, "checkout", "-b", "extra-branch", self.first)
        (self.upstream / "branch-only.txt").write_text("other branch", encoding="utf-8")
        branch_commit = self.commit("other branch")
        self.git("-C", self.upstream, "tag", "-a", "cache-tag", "-m", "annotated tag")
        self.git("-C", self.upstream, "update-ref", "refs/branch-heads/1234", branch_commit)
        self.git("-C", self.upstream, "checkout", current_branch)
        return {ref: self.git("-C", self.upstream, "rev-parse", ref) for ref in (
            "refs/heads/extra-branch", "refs/tags/cache-tag", "refs/branch-heads/1234")}

    def project(self, name):
        project = self.directory / name
        project.mkdir()
        return project

    def cache_has_object(self, object_id, git_dir=None):
        return subprocess.run(
            ["git", "--git-dir=" + str(git_dir or self.cache), "cat-file", "-e", object_id],
            capture_output=True,
            env=dict(os.environ, GIT_NO_LAZY_FETCH="1")).returncode == 0

    def assert_complete_cache(self):
        with patch.dict(os.environ, {"GIT_NO_LAZY_FETCH": "1"}):
            objects = self.git("--git-dir=" + str(self.cache), "rev-list", "--objects",
                               "--missing=print", "--no-object-names", "--all")
        self.assertFalse(any(line.startswith("?") for line in objects.splitlines()))
        self.assertEqual(
            self.git("--git-dir=" + str(self.cache), "rev-parse", "--is-shallow-repository"),
            "false")

    def test_without_environment_uses_local_cache_despite_git_config(self):
        configured_cache = self.directory / "configured cache"
        global_config = self.directory / "gitconfig"
        self.git("config", "--file", global_config, "cache.cachepath", configured_cache)
        second = self.second_commit()
        project = self.project("project")
        with patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(global_config)}):
            os.environ.pop("GIT_CACHE_PATH", None)
            sync_chromium.sync_source(project, second)

        local_cache = project / ".chromium.git"
        self.assertTrue(self.cache_has_object(second, git_dir=local_cache))
        self.assertFalse(self.cache_has_object(self.first, git_dir=local_cache))
        self.assertEqual((project / "base" / "source.cc").read_text(), "second base")
        self.assertEqual(
            self.git("--git-dir=" + str(local_cache), "rev-parse", "--is-shallow-repository"),
            "true")
        for path in (".gn", "chrome/browser.cc", "third_party/blink/source.cc"):
            object_id = self.git("-C", self.upstream, "rev-parse", second + ":" + path)
            self.assertFalse(self.cache_has_object(object_id, git_dir=local_cache), path)
        self.assertFalse(configured_cache.exists())
        self.assertFalse(self.cache_root.exists())

    def test_populates_full_cache_and_reuses_it_across_projects(self):
        extra_refs = self.extra_refs()
        first_project = self.project("first-project")
        sync_chromium.sync_source(first_project, self.first)
        self.assertEqual((first_project / "base" / "source.cc").read_text(), "first base")
        self.assertEqual((first_project / "third_party" / "README.md").read_text(),
                         "imported third party metadata")
        self.assertFalse((first_project / "third_party" / "blink").exists())
        self.assertFalse((first_project / "chrome" / "browser.cc").exists())
        self.assertFalse((first_project / ".gn").exists())

        # Shared caches contain complete Chromium source, including files that
        # this project does not import into its worktree.
        for path in ("base/source.cc", "chrome/VERSION", "third_party/README.md",
                     "third_party/dependency/source.cc"):
            object_id = self.git("-C", self.upstream, "rev-parse", self.first + ":" + path)
            self.assertTrue(self.cache_has_object(object_id), path)
        for path in (".gn", "chrome/browser.cc", "third_party/blink/source.cc"):
            object_id = self.git("-C", self.upstream, "rev-parse", self.first + ":" + path)
            self.assertTrue(self.cache_has_object(object_id), path)
        for ref, object_id in extra_refs.items():
            self.assertEqual(self.git("--git-dir=" + str(self.cache), "rev-parse", ref), object_id)
        branch_blob = self.git("-C", self.upstream, "rev-parse", "extra-branch:branch-only.txt")
        self.assertTrue(self.cache_has_object(branch_blob))
        self.assert_complete_cache()
        cache_head = (self.cache / "HEAD").read_bytes()
        self.assertFalse((self.cache / "index").exists())
        self.assertEqual(
            self.git("--git-dir=" + str(self.cache), "rev-parse",
                     "refs/chromium-base/" + self.first), self.first)

        second = self.second_commit()
        self.assertFalse(self.cache_has_object(second))
        sync_chromium.sync_source(first_project, second)
        self.assertTrue(self.cache_has_object(second))
        self.assertEqual((first_project / "base" / "source.cc").read_text(), "second base")
        second_blob = self.git("-C", self.upstream, "rev-parse", second + ":base/source.cc")
        self.assertTrue(self.cache_has_object(second_blob))
        self.assert_complete_cache()
        project_head = self.git("--git-dir=" + str(first_project / ".chromium.git"),
                                "rev-parse", "HEAD")

        second_project = self.project("second-project")
        with patch.object(sync_chromium, "CHROMIUM_URL", "file:///does-not-exist"):
            sync_chromium.sync_source(second_project, self.first)
            sync_chromium.sync_source(first_project, second)
        self.assertEqual((second_project / "base" / "source.cc").read_text(), "first base")
        self.assertEqual((first_project / "base" / "source.cc").read_text(), "second base")
        self.assertEqual(
            self.git("--git-dir=" + str(first_project / ".chromium.git"),
                     "rev-parse", "HEAD"), project_head)
        self.assertEqual((self.cache / "HEAD").read_bytes(), cache_head)
        self.assertFalse((self.cache / "index").exists())
        self.assertEqual(
            self.git("--git-dir=" + str(self.cache), "rev-parse",
                     "refs/chromium-base/" + second), second)
        self.assertEqual(
            self.git("--git-dir=" + str(self.cache), "rev-parse",
                     "refs/chromium-base/" + self.first), self.first)
        alternates = first_project / ".chromium.git" / "objects" / "info" / "alternates"
        self.assertEqual(alternates.read_bytes(),
                         ((self.cache / "objects").as_posix() + "\n").encode("utf-8"))

    def test_migrates_shallow_partial_cache_even_when_target_is_present(self):
        extra_refs = self.extra_refs()
        second = self.second_commit()
        self.git("clone", "--bare", "--depth=1", "--filter=blob:none",
                 "--single-branch", "--no-tags", self.upstream.as_uri(), self.cache)
        self.assertTrue(self.cache_has_object(second))
        self.assertFalse(self.cache_has_object(self.first))
        blink_blob = self.git("-C", self.upstream, "rev-parse", second + ":third_party/blink/source.cc")
        self.assertFalse(self.cache_has_object(blink_blob))

        project = self.project("project")
        sync_chromium.sync_source(project, second)
        self.assert_complete_cache()
        self.assertTrue(self.cache_has_object(self.first))
        self.assertTrue(self.cache_has_object(blink_blob))
        old_blob = self.git("-C", self.upstream, "rev-parse", self.first + ":base/source.cc")
        self.assertTrue(self.cache_has_object(old_blob))
        for ref, object_id in extra_refs.items():
            self.assertEqual(self.git("--git-dir=" + str(self.cache), "rev-parse", ref), object_id)
        self.assertEqual((project / "base" / "source.cc").read_text(), "second base")
        self.assertFalse((project / "third_party" / "blink").exists())
        with patch.object(sync_chromium, "CHROMIUM_URL", "file:///does-not-exist"):
            sync_chromium.sync_source(self.project("offline-project"), self.first)

    def test_switching_caches_populates_the_new_cache(self):
        project = self.project("project")
        sync_chromium.sync_source(project, self.first)
        new_cache_root = self.directory / "new cache root"
        new_cache = new_cache_root / "chromium.googlesource.com-chromium-src"
        with patch.dict(os.environ, {"GIT_CACHE_PATH": str(new_cache_root)}):
            # The existing checkout can read objects from its old alternates,
            # but the newly selected cache must also receive those objects.
            sync_chromium.sync_source(project, self.first)
            blob = self.git("-C", self.upstream, "rev-parse", self.first + ":base/source.cc")
            self.assertTrue(self.cache_has_object(blob, git_dir=new_cache))
            fresh_project = self.project("fresh-project")
            with patch.object(sync_chromium, "CHROMIUM_URL", "file:///does-not-exist"):
                sync_chromium.sync_source(fresh_project, self.first)
            self.assertEqual((fresh_project / "base" / "source.cc").read_text(), "first base")

        alternates = project / ".chromium.git" / "objects" / "info" / "alternates"
        self.assertEqual(alternates.read_text().splitlines(), [
            (self.cache / "objects").as_posix(),
            (new_cache / "objects").as_posix(),
        ])

    def test_updating_full_cache_preserves_head_index_and_history(self):
        self.git("clone", "--mirror", self.upstream.as_uri(), self.cache)
        self.git("--git-dir=" + str(self.cache), "config", "--unset-all", "remote.origin.fetch")
        for refspec in ("+refs/heads/*:refs/heads/*",
                        "+refs/branch-heads/*:refs/branch-heads/*",
                        "+refs/tags/*:refs/tags/*"):
            self.git("--git-dir=" + str(self.cache), "config", "--add", "remote.origin.fetch", refspec)
        original_fetch = self.git("--git-dir=" + str(self.cache), "config", "--get-all",
                                  "remote.origin.fetch")
        self.git("--git-dir=" + str(self.cache), "config", "user.name", "Cache owner")
        self.git("--git-dir=" + str(self.cache), "read-tree", self.first)
        (self.cache / "FETCH_HEAD").write_text("existing fetch metadata\n", encoding="utf-8")
        original = {name: (self.cache / name).read_bytes()
                    for name in ("HEAD", "index", "FETCH_HEAD")}
        second = self.second_commit()
        project = self.project("project")
        sync_chromium.sync_source(project, second)

        self.assertEqual((project / "base" / "source.cc").read_text(), "second base")
        for name, contents in original.items():
            self.assertEqual((self.cache / name).read_bytes(), contents, name)
        self.assertEqual(
            self.git("--git-dir=" + str(self.cache), "rev-parse", "HEAD"), second)
        self.assertEqual(
            self.git("--git-dir=" + str(self.cache), "rev-parse", "--is-shallow-repository"),
            "false")
        self.git("--git-dir=" + str(self.cache), "merge-base", "--is-ancestor", self.first, second)
        self.assertEqual(
            self.git("--git-dir=" + str(self.cache), "config", "user.name"), "Cache owner")

        # Upstream ref updates must not inherit pruning that would remove pins
        # for old project snapshots, which do not exist on the remote.
        snapshot_tree = self.git("--git-dir=" + str(project / ".chromium.git"),
                                 "rev-parse", "HEAD^{tree}")
        snapshot_ref = "refs/chromium-base/trees/" + snapshot_tree
        self.git("--git-dir=" + str(self.cache), "config", "fetch.prune", "true")
        self.git("--git-dir=" + str(self.cache), "config", "fetch.pruneTags", "true")
        (self.upstream / "base" / "source.cc").write_text("third base", encoding="utf-8")
        third = self.commit("third")
        sync_chromium.sync_source(self.project("new-project"), third)
        self.assertEqual(
            self.git("--git-dir=" + str(self.cache), "rev-parse", snapshot_ref), snapshot_tree)
        self.assertEqual(
            self.git("--git-dir=" + str(self.cache), "config", "--get-all", "remote.origin.fetch"),
            original_fetch)

        # Cache cleanup must retain the synthetic trees borrowed by snapshots.
        self.git("--git-dir=" + str(self.cache), "prune", "--expire=now")
        with patch.dict(os.environ, {"GIT_NO_LAZY_FETCH": "1"}):
            for path, contents in (("base/source.cc", "second base"),
                                   ("chrome/VERSION", "second version")):
                self.assertEqual(
                    self.git("--git-dir=" + str(project / ".chromium.git"),
                             "show", "HEAD:" + path), contents)


if __name__ == "__main__":
    unittest.main()
