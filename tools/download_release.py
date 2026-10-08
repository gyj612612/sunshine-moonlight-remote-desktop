#!/usr/bin/env python3
"""Download an exact official release asset, verified with GitHub's SHA-256."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request


REPOSITORIES = {
    "sunshine": "LizardByte/Sunshine",
    "moonlight": "moonlight-stream/moonlight-qt",
}
TARGETS = {
    "moonlight": {
        "macos": r"Moonlight-[0-9][^/]*\.dmg",
        "windows": r"MoonlightSetup-[0-9][^/]*\.exe",
        "windows-arm64": r"MoonlightPortable-arm64-[0-9][^/]*\.zip",
        "linux-x64": r"Moonlight-[0-9][^/]*-x86_64\.AppImage",
    },
    "sunshine": {
        "windows-x64": r"Sunshine-Windows-AMD64-installer\.msi",
        "windows-arm64": r"Sunshine-Windows-ARM64-installer\.msi",
        "macos-arm64": r"Sunshine-macOS-arm64\.dmg",
        "macos-x64": r"Sunshine-macOS-x86_64\.dmg",
        "linux-x64": r"Sunshine_[0-9][^/]*_x86_64\.AppImage",
        "linux-arm64": r"Sunshine_[0-9][^/]*_aarch64\.AppImage",
    },
}
for ubuntu in ("22.04", "24.04"):
    for arch in ("amd64", "arm64"):
        TARGETS["sunshine"]["ubuntu" + ubuntu + "-" + arch] = (
            r"sunshine_[^/]+\+ubuntu" + re.escape(ubuntu) + "_" + arch + r"\.deb"
        )

ALLOWED_HOSTS = {
    "api.github.com", "github.com", "release-assets.githubusercontent.com",
    "objects.githubusercontent.com",
}


def validate_url(url):
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS
            or parsed.username or parsed.password or parsed.port not in (None, 443)):
        raise ValueError("Only official GitHub HTTPS endpoints are accepted")


class OfficialRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def open_url(url, direct=False):
    validate_url(url)
    handlers = [OfficialRedirectHandler()]
    if direct:
        handlers.append(urllib.request.ProxyHandler({}))
    opener = urllib.request.build_opener(*handlers)
    return opener.open(urllib.request.Request(url, headers={
        "User-Agent": "sunshine-moonlight-release-downloader",
    }), timeout=60)


def select_asset(release, component, target):
    pattern = TARGETS.get(component, {}).get(target)
    if pattern is None:
        raise ValueError("Unsupported component/target combination")
    matches = [a for a in release.get("assets", [])
               if re.fullmatch(pattern, a.get("name", ""))]
    if len(matches) != 1:
        raise ValueError("Expected one official asset; found " + str(len(matches)))
    asset = matches[0]
    name = asset["name"]
    if name != Path(name).name or "\\" in name or ".." in name:
        raise ValueError("Unsafe asset filename")
    if not re.fullmatch(r"sha256:[a-fA-F0-9]{64}", asset.get("digest") or ""):
        raise ValueError("Official SHA-256 digest is missing; refusing unverified download")
    url = asset.get("browser_download_url", "")
    validate_url(url)
    expected_prefix = "https://github.com/" + REPOSITORIES[component] + "/releases/download/"
    if not url.startswith(expected_prefix):
        raise ValueError("Asset URL does not belong to the official project")
    if not isinstance(asset.get("size"), int) or asset["size"] <= 0:
        raise ValueError("Invalid asset size")
    return asset


def download_asset(asset, directory, opener=open_url):
    destination = Path(directory)
    destination.mkdir(parents=True, exist_ok=True)
    final = destination / asset["name"]
    if final.exists() or final.is_symlink():
        raise ValueError("Destination already exists; refusing to overwrite")
    temporary = None
    try:
        digest = hashlib.sha256()
        size = 0
        with tempfile.NamedTemporaryFile(dir=destination, prefix=".download-", delete=False) as output:
            temporary = Path(output.name)
            with opener(asset["browser_download_url"]) as source:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > asset["size"]:
                        raise ValueError("Download exceeds official asset size")
                    digest.update(chunk)
                    output.write(chunk)
        if size != asset["size"] or digest.hexdigest() != asset["digest"][7:].lower():
            raise ValueError("SHA-256 or size mismatch; download discarded")
        # Hard-link creation is atomic and refuses a concurrently created destination.
        os.link(temporary, final)
        return final
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, epilog="Targets: " + str(TARGETS))
    parser.add_argument("component", choices=REPOSITORIES)
    parser.add_argument("target")
    parser.add_argument("--tag", help="Exact upstream release tag; default: latest stable")
    parser.add_argument("--download", metavar="DIRECTORY", help="Download only; never install or run")
    parser.add_argument("--direct", action="store_true", help="Bypass proxy for this command only")
    args = parser.parse_args(argv)
    try:
        if args.target not in TARGETS[args.component]:
            raise ValueError("Unsupported target. Choose: " + ", ".join(TARGETS[args.component]))
        suffix = "latest" if not args.tag else "tags/" + urllib.parse.quote(args.tag, safe="")
        api_url = "https://api.github.com/repos/" + REPOSITORIES[args.component] + "/releases/" + suffix
        with open_url(api_url, direct=args.direct) as response:
            release = json.load(response)
        if release.get("draft") or release.get("prerelease"):
            raise ValueError("Only non-draft, stable releases are accepted")
        asset = select_asset(release, args.component, args.target)
        print("Release:", release["tag_name"])
        print("Asset:", asset["name"])
        print("SHA-256:", asset["digest"][7:])
        if args.download:
            print("Verified download:", download_asset(
                asset, args.download, opener=lambda url: open_url(url, direct=args.direct)))
        else:
            print("Preview only. Add --download DIRECTORY to download.")
        return 0
    except urllib.error.HTTPError as error:
        if error.code in (403, 429) and error.headers.get("X-RateLimit-Remaining") == "0":
            parser.exit(1, "GitHub public API rate limit reached. Wait, use the official release page, or try --direct on an allowed direct network.\n")
        parser.exit(1, "GitHub HTTP error " + str(error.code) + "; no download installed.\n")
    except (ValueError, OSError, urllib.error.URLError, KeyError) as error:
        # Do not emit signed redirect URLs or authentication/network environment data.
        if isinstance(error, (OSError, urllib.error.URLError)):
            parser.exit(1, "Download/network/filesystem error; check connectivity and permissions.\n")
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
