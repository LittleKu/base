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
            (mirror / "objects").mkdir(parents=True)
            with patch.dict(os.environ, {"GIT_CACHE_PATH": temporary}):
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
            with (patch.object(sync_chromium, "CHROMIUM_URL", "file:///does-not-exist"),
                  patch.object(sync_chromium, "find_git_cache", return_value=upstream / ".git")):
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


if __name__ == "__main__":
    unittest.main()
