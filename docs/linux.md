# Linux 被控端注意事项

## 会话与硬件

Sunshine 需要能捕获的图形会话及可用的编码器，单纯 SSH 在线不代表桌面可以串流。
X11、Wayland、KMS、Portal 的要求不同，按当前上游文档选择捕获方式。
无显示器机器可能需要支持的虚拟显示方案或硬件显示模拟器；不要盲目覆盖 Xorg 配置。

用户服务必须属于实际登录桌面的用户。
从图形终端启动时通常不需要硬编码 DISPLAY/XAUTHORITY；
必要时可在该图形终端中将现有会话变量导入用户服务管理器：

```bash
systemctl --user import-environment DISPLAY XAUTHORITY XDG_SESSION_TYPE XDG_CURRENT_DESKTOP
systemctl --user restart app-dev.lizardbyte.app.Sunshine.service
```

不要把这个命令放进另一位用户的 SSH 会话，不要把真实运行时路径提交到仓库。
上述导入不跨重启持久化；显示管理器变化后应重新验证。
用户服务不等于系统级无人登录服务；本仓库不配置自动登录或修改登录密码。

## 现有配置

`examples/sunshine.conf.example` 只是需要人工合并的设置参考，不是安装脚本。
不要直接覆盖 `~/.config/sunshine/sunshine.conf`。
修改前在本机受保护的位置备份，修改后逐项验证；备份不能上传 GitHub。
已有用户、配对、apps.json、插件或显示设置均应保留。

托盘启动确实出现崩溃时，才考虑在该用户配置中设置 `system_tray = disabled`。
这只影响 Sunshine 托盘/通知，不应修改系统 Qt、桌面或其他应用环境。

## 安全排查

可在本机运行以下只读检查；输出可能包含用户路径或网络信息，不要直接公开：

```bash
systemctl --user status app-dev.lizardbyte.app.Sunshine.service --no-pager
journalctl --user -u app-dev.lizardbyte.app.Sunshine.service -n 40 --no-pager
```

编码器初始化测试中的错误不一定意味着连接失败，应结合最终选中的编码器和真实画面判断。
不要为了单条警告就升级整机驱动、重启或杀掉科研进程。
不要使用 sudo 启动 Sunshine 桌面程序，也不要授予无关目录或设备全局写权限。
