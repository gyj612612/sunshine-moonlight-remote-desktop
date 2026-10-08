# Windows 控制端

Windows 可以连接 Ubuntu 上的 Sunshine，操作的是同一个 Ubuntu 用户桌面，
不是另建 RDP 会话；Windows 上只需要 Moonlight，不需要再安装 Sunshine。

## 首次连接

1. 从 [Moonlight 官方发布页](https://github.com/moonlight-stream/moonlight-qt/releases/latest)
   下载 Windows 安装器，或用本仓库的校验下载工具。
2. 检查安装器来源和 Windows 签名提示，完成安装。不要关闭 SmartScreen。
3. 在 Windows 连接能访问工作站的校园/办公 VPN，或接入同一局域网。
4. 启动 Moonlight，点击添加电脑，填写工作站地址，不填写 Sunshine 管理页面 URL。
5. 点主机发起配对，记录本次显示的 PIN。
6. 在被控端本机 Sunshine 管理页核对请求，输入 PIN，再在 Windows 选择 Desktop。

Mac 和 Windows 各自配对。不要复制 Mac 的应用数据、证书或钥匙串到 Windows。
GitHub 仓库不包含任何配对资料，克隆仓库不代表获得物理机访问权限。

## 每次使用

- 连接：先保证网络可达，再 Moonlight → 主机 → Desktop。
- 断开：Ctrl + Alt + Shift + Q，只断开画面，服务器上的任务继续运行。
- 最小化：Ctrl + Alt + Shift + D。
- 卡顿：先设 60 FPS、15–25 Mbps，再查看性能统计，避免一开始使用 4K/120 FPS。
- 同时多端操作可能争抢同一桌面的鼠标键盘；避免同时从 Mac、Windows、其他远程工具输入。

## Windows 也作为被控端

在 Windows 安装与 CPU 架构匹配的官方 Sunshine，其他设备使用 Moonlight 连接。
仅允许所需、可信网络范围的入站规则，不要一键关闭防火墙。
Windows ARM64 Sunshine 目前存在上游实验性限制，不能假定与 x64 等效。
可选虚拟手柄/输入驱动并非普通桌面连接的必选安装项，某些组件可能收费。
