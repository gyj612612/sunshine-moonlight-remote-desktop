# 安装与连接

## 被控端：Sunshine

### Ubuntu / Linux

从 [官方发布页](https://github.com/LizardByte/Sunshine/releases/latest) 或下方下载工具
获取与 Ubuntu 版本、CPU 架构匹配的安装包。在被控电脑上安装：

```bash
sudo apt install ./downloads/sunshine_*.deb
```

目录中只保留一个选定的 deb，避免同时安装多个版本。
安装器可能添加依赖、udev 规则及捕获权限。安装前查看官方说明，不必为此升级整机显卡驱动。

在需要共享的用户的**图形桌面终端**里启动：

```bash
systemctl --user start app-dev.lizardbyte.app.Sunshine.service
```

确认连接成功后，可选择随该用户图形会话启动：

```bash
systemctl --user enable app-dev.lizardbyte.app.Sunshine.service
```

停止或取消自动启动：

```bash
systemctl --user stop app-dev.lizardbyte.app.Sunshine.service
systemctl --user disable app-dev.lizardbyte.app.Sunshine.service
```

用户服务不等于开机自动登录。SSH 会话变量、X11/Wayland 和无显示器场景见 [Linux 说明](linux.md)。

### Windows

使用官方 Sunshine MSI，选择正确的 x64 或 ARM64 版本并审阅安装选项。
ARM64 有实验性限制。可选输入/手柄驱动不是普通桌面操作的必装项。
防火墙仅允许必要、可信的网络范围，不要直接关闭防火墙。

### macOS

使用与 Intel / Apple Silicon 匹配的 Sunshine DMG，按系统提示由用户确认必要权限。
macOS 被控端属实验支持。保留其他恢复通道，不要绕过 Gatekeeper 或系统权限提示。

## 控制端：Moonlight

从 [官方发布页](https://github.com/moonlight-stream/moonlight-qt/releases/latest)
获取 Windows 安装器、macOS DMG 或 Linux 客户端。移动设备使用对应的官方应用。
安装 Moonlight 的电脑不需要再安装 Sunshine，除非它也要共享自己的桌面。

## 配对

1. 确认两端网络互通；跨网时先连接获准的 VPN/组网。
2. 在被控端本机打开 `https://localhost:47990`，创建独立的管理凭据。
3. 管理页使用自签证书。按官方文档核对来源及证书，由用户本人处理浏览器提示，不关闭证书校验。
4. 在 Moonlight 添加被控电脑地址，点击主机发起配对。
5. 在 Sunshine 管理页核对请求，提交 Moonlight 显示的 PIN。
6. 选择 Desktop 连接。每台新控制端独立配对，不共享配对证书。

不公开管理端口 47990，不将密码、证书、应用状态或故障截图提交到 Git。
现有 `~/.config/sunshine` 应保留；示例配置只作参考，不直接覆盖。

## 下载工具

要求 Python 3.9+；Windows 通常使用 `py -3`，Mac/Linux 使用 `python3`。
无 `--download` 时只预览，不保存文件；所有模式都不自动安装。

```bash
python3 tools/download_release.py moonlight macos
python3 tools/download_release.py moonlight windows --download downloads
python3 tools/download_release.py moonlight windows-arm64 --download downloads
python3 tools/download_release.py moonlight linux-x64 --download downloads
python3 tools/download_release.py sunshine ubuntu24.04-arm64 --download downloads
python3 tools/download_release.py sunshine windows-x64 --download downloads
python3 tools/download_release.py sunshine macos-arm64 --download downloads
```

`--tag RELEASE_TAG` 固定官方稳定版本；`--help` 查看全部支持的目标。
缺少官方 SHA-256、大小不符或校验失败时停止下载；不覆盖已有文件，不接受第三方镜像。
校验用于匹配官方发布资产，不能替代独立的作者签名验证。

公共 GitHub API 限流时可等待或改用官方发布页，不需要提供 token。
如果代理出口被限流且本地允许直连，可添加 `--direct`，仅对本次命令绕过代理。

## 画质与快捷键

先用 1080p / 60 FPS / 15–25 Mbps，再按带宽和文字清晰度调整。
编码器、显示模式、网络、客户端解码及屏幕刷新率共同决定体验。
60 Hz 屏幕不能显示真正的 120 Hz 动态画面，放大低分辨率串流也不等于原生 4K。

| 操作 | Windows / Linux | Mac |
| --- | --- | --- |
| 断开并保留远端程序 | Ctrl + Alt + Shift + Q | Control + Option + Shift + Q |
| 最小化 | Ctrl + Alt + Shift + D | Control + Option + Shift + D |
| 性能统计 | Ctrl + Alt + Shift + S | Control + Option + Shift + S |

跨网连接需要真实入站可达性，单纯查到公网出口 IP 不够。
不要自动打开 UPnP、全网防火墙或路由映射；公网部署需经网络管理员批准。
