# Bilibili Live Activity Check-in

Python 示例脚本：针对**指定且有效的 B站直播活动**检查当日签到状态，并在符合条件时发起签到请求。

> **重要**：这不是全站通用签到或自动升级工具。B站活动接口和资格限制可能随时变化，代码尚未在你的账号与实际活动上完成端到端验证。不保证积分、经验或奖励到账。

## 准备工作

- Python 3.9+
- 你本人的 B站账号与有效直播活动
- 仅在你有权使用的账号和活动中运行

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

## Windows PowerShell 运行

在你自己的电脑设置**进程级**环境变量（不要把真实 Cookie 写入代码或提交到 GitHub）：

```powershell
$env:BILI_COOKIE = "SESSDATA=你的值; bili_jct=你的值"
$env:BILI_ACTIVITY_ID = "实际有效活动ID"
$env:BILI_RUIDS = "主播UID"
python .\bilibili_sign.py
```

多个主播 UID 使用逗号分隔。实际接口能否工作取决于对应活动规则及接口状态，主播 UID 与活动 ID 并非随意组合。

## 自动执行

可通过 Windows **任务计划程序**定时启动脚本。任务运行用户必须能读取上述环境变量；PowerShell 会话中设置的 `$env:...` 不会自动持久化到定时任务。请使用你自己管理的安全凭证存储或任务运行用户的安全环境配置方式，避免在任务命令行暴露 Cookie。

## 安全提醒

- `SESSDATA` 是登录凭证，`bili_jct` 用于 CSRF 验证，请勿公开分享。
- **不要**把真实 Cookie 写入 `.env.example`、Issue、日志、GitHub Actions 工作流或公开仓库。
- 截图时遮挡任何 Cookie 值；泄露后应退出相关会话并重新登录。
- 脚本会检查登录状态、活动条件与签到状态；不是平台提供的官方 SDK，运行结果需在活动页面确认。

## 退出码

- `0`：处理完毕，未遇到已捕获的请求错误（不代表一定领取奖励）
- `1`：登录或请求失败
- `2`：缺少配置或参数无效

## 免责声明

仅用于学习和管理自己的合法账号；请遵守 B站服务条款与活动规则。接口变更时应停止自动请求并核对最新活动要求。
