# Sunshine + Moonlight

[中文](README.md) · **English**

![Sunshine + Moonlight: free and open-source cross-platform remote desktop](assets/cover.png)

Access a full remote desktop from a Mac, Windows PC, or Linux computer.
**Sunshine shares the desktop. Moonlight displays it and sends your input.**

Free and open source · Hardware accelerated · Cross-platform

## Platforms

| | Client · Moonlight | Host · Sunshine |
| --- | --- | --- |
| Windows | Supported | Supported; ARM64 has experimental limitations |
| macOS | Intel and Apple Silicon | Experimental |
| Linux | Supported | Requires a compatible desktop session and graphics driver |
| Phones, tablets, Apple TV | Platform-specific Moonlight apps | — |

For coding, everyday desktop work, and remote workstations.
Image quality and latency depend on your hardware, display, and network.

## Connect in Three Steps

1. **Install:** [Sunshine](https://github.com/LizardByte/Sunshine/releases/latest) on the remote computer and [Moonlight](https://github.com/moonlight-stream/moonlight-qt/releases/latest) on your client.
2. **Pair:** Ensure network reachability, add the host in Moonlight, and approve its PIN in the host's local Sunshine administration page.
3. **Connect:** Choose **Desktop**. Press `Ctrl + Alt + Shift + Q` to disconnect without stopping remote programs. On Mac, use `Option` for `Alt`.

[Setup guide, Chinese](docs/setup.md) · [Windows guide, Chinese](docs/windows.md) · [Linux notes, Chinese](docs/linux.md)

## Official Release Downloader

Python 3.9+, no third-party dependencies. Selects the latest stable release and verifies its official SHA-256 digest. **Downloads only; never installs or runs an installer.**

```bash
# macOS client
python3 tools/download_release.py moonlight macos --download downloads

# Ubuntu 22.04 x64 host
python3 tools/download_release.py sunshine ubuntu22.04-amd64 --download downloads
```

```powershell
# Windows client
py -3 tools/download_release.py moonlight windows --download downloads
```

Use `--help` for targets, `--tag RELEASE_TAG` to pin a stable version,
and `--direct` to bypass proxies for that command only when your network permits it.
Public API rate limits may apply. No token is required; the official release pages are an alternative.

## Network and Quality

Start with **1080p / 60 FPS / 15–25 Mbps** and adjust to your display and connection.
Match stream resolution to the host desktop. Higher settings do not guarantee lower latency.

**Use a reachable LAN, an authorized VPN/overlay network, or approved public inbound routing.**
There is no built-in public relay. An outbound public IP does not imply inbound reachability.
Keep the administration interface private. This repository does not change firewall rules, routes, or system proxies.

## Documentation and License

[Moonlight guide](https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide) · [Sunshine documentation](https://docs.lizardbyte.dev/projects/sunshine/latest/)

Independent helper scripts, examples, and documentation. No upstream binaries or device configuration are bundled.
Original code and documentation use the [MIT License](LICENSE); upstream software retains its own licenses.
Basic desktop streaming is free; optional drivers and third-party services may have separate fees.

Tests: `python3 -m unittest discover -s tests -v` · Publication check: `python3 tools/check_privacy.py`
