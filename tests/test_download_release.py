import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "download_release", Path(__file__).resolve().parents[1] / "tools/download_release.py"
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def make_asset(name="Moonlight-1.2.3.dmg", content=b"test asset", component="moonlight"):
    return {
        "name": name,
        "size": len(content),
        "digest": "sha256:" + hashlib.sha256(content).hexdigest(),
        "browser_download_url": "https://github.com/" + module.REPOSITORIES[component]
        + "/releases/download/v1.2.3/" + name,
    }


class ReleaseTests(unittest.TestCase):
    def test_supported_assets(self):
        samples = [
            ("moonlight", "macos", "Moonlight-1.2.3.dmg"),
            ("moonlight", "windows", "MoonlightSetup-1.2.3.exe"),
            ("moonlight", "windows-arm64", "MoonlightPortable-arm64-1.2.3.zip"),
            ("moonlight", "linux-x64", "Moonlight-1.2.3-x86_64.AppImage"),
            ("sunshine", "windows-x64", "Sunshine-Windows-AMD64-installer.msi"),
            ("sunshine", "windows-arm64", "Sunshine-Windows-ARM64-installer.msi"),
            ("sunshine", "macos-arm64", "Sunshine-macOS-arm64.dmg"),
            ("sunshine", "macos-x64", "Sunshine-macOS-x86_64.dmg"),
            ("sunshine", "linux-x64", "Sunshine_1.2.3_x86_64.AppImage"),
            ("sunshine", "linux-arm64", "Sunshine_1.2.3_aarch64.AppImage"),
        ]
        for version in ("22.04", "24.04"):
            for arch in ("amd64", "arm64"):
                samples.append(("sunshine", "ubuntu" + version + "-" + arch,
                                "sunshine_1.2.3-1+ubuntu" + version + "_" + arch + ".deb"))
        for component, target, name in samples:
            with self.subTest(target=target):
                asset = make_asset(name, component=component)
                self.assertEqual(module.select_asset({"assets": [asset]}, component, target), asset)

    def test_missing_and_ambiguous_assets(self):
        for assets in ([], [make_asset(), make_asset()]):
            with self.assertRaises(ValueError):
                module.select_asset({"assets": assets}, "moonlight", "macos")

    def test_missing_digest(self):
        asset = make_asset()
        asset["digest"] = None
        with self.assertRaises(ValueError):
            module.select_asset({"assets": [asset]}, "moonlight", "macos")

    def test_wrong_project(self):
        asset = make_asset()
        asset["browser_download_url"] = "https://github.com/untrusted/project/releases/download/v1/file"
        with self.assertRaises(ValueError):
            module.select_asset({"assets": [asset]}, "moonlight", "macos")

    def test_unsafe_urls(self):
        for url in ("http://github.com/file", "https://github.com.evil.example/file",
                    "https://user:secret@github.com/file", "https://github.com:123/file",
                    "file:///etc/passwd"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                module.validate_url(url)

    def test_download_success(self):
        content = b"test asset"
        with tempfile.TemporaryDirectory() as directory:
            path = module.download_asset(make_asset(content=content), directory,
                                         opener=lambda url: io.BytesIO(content))
            self.assertEqual(path.read_bytes(), content)
            self.assertEqual(len(list(Path(directory).iterdir())), 1)

    def test_corrupt_truncated_and_oversized(self):
        for content in (b"corruption", b"short", b"too much data here"):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(ValueError):
                    module.download_asset(make_asset(), directory, opener=lambda url: io.BytesIO(content))
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_existing_file_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / make_asset()["name"]
            path.write_bytes(b"keep existing")
            with self.assertRaises(ValueError):
                module.download_asset(make_asset(), directory)
            self.assertEqual(path.read_bytes(), b"keep existing")

    def test_network_failure_cleans_partial_file(self):
        def failure(url):
            raise OSError("test failure")

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OSError):
                module.download_asset(make_asset(), directory, opener=failure)
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
