# 贴吧回贴批量删除工具

批量删除你在百度贴吧发过的所有「回贴」。不碰密码，提供两种模式：稳定的 UI 自动化版，和极快的接口加速版。

> ⚠️ 仅限删除**你自己账号**的内容，请勿用于删除他人内容或任何违规用途。

---

## 解决了什么问题

百度贴吧没有「一键清空回贴」的功能。想清掉以前发过的大量回贴，只能手动逐条「… → 删除 → 确定」，几百上千条会点到怀疑人生。

本工具连接一个**你已经登录的 Edge 浏览器**，自动重复执行删除。账号密码始终只由你自己在浏览器里输入——代码里不出现、不落盘任何登录凭据（BDUSS / STOKEN / Cookie 一律不碰）。

---

## 两种模式

| | `main.py` | `fast_mode.py` ★ |
|---|---|---|
| 原理 | 模拟点击页面按钮 | 直接调用贴吧接口 |
| 单条耗时 | 10~15 秒 | 2~4 秒 |
| 依赖 | 页面 DOM（改版要重抓定位） | 接口签名（接口变了要改密钥） |
| 定位 | 兜底、求稳 | 主力，推荐 |

**一般直接上接口加速版。** `main.py` 作为接口签名失效时的兜底保留。

---

## 接口加速版（fast_mode.py）

核心思路：不操作页面 DOM，而是在登录态的浏览器内部用 `fetch` 直接调贴吧接口。浏览器自动携带 Cookie，所以全程无需手动搬运登录态，也从源头杜绝了凭据泄露。

### 用到的接口

| 接口 | 用途 |
|---|---|
| `/c/u/feed/myThread` | 翻页拉取「我的回贴」列表 |
| `/c/c/bawu/delpost_pc` | 删除一条回贴 |
| `/c/s/pc/sync` | 获取 `tbs`（CSRF token） |

### 数据流与字段映射

1. `myThread` 返回每条回贴的三个关键字段：
   - `post_info.id` → 回贴 ID
   - `thread_info.tid` → 帖子 ID
   - `thread_info.fid` → 吧 ID
2. 删除时映射到 `delpost_pc`：`post_info.id → pid`、`thread_info.tid → z`、`thread_info.fid → fid`，再带上 `tbs` 和 `sign`。
3. 响应 `error_code: "0"` 即删除成功。

列表接口负责「给原料」，删除接口拿这些原料「干活」，两者是一套。

### 签名（sign）

`myThread` 和 `delpost_pc` 都要求带 `sign` 签名。算法：

```
sign = md5( join_sorted("k=v") + SIGN_SECRET )
```

即：所有参数按 key 升序拼成 `k=v` 串（无分隔符，跳过 `sign`/`sig`/`None`），末尾追加密钥，再做 MD5（小写）。

密钥为贴吧 PC 端通用常量（`SIGN_SECRET = "36770b1f34c9bbf2e7d1a99d2b82fa9e"`，见代码顶部）。该算法已在真实请求上逐字节验证通过。

### 用法

```powershell
uv run fast_mode.py --list-only   # 只统计回帖数量，不删除
uv run fast_mode.py --limit 3     # 只删 3 条就停（试跑）
uv run fast_mode.py               # 连续删除
```

### 连续模式与风控

不带 `--limit` 时进入**连续模式**：每轮拉取当前最前面的约 20 条、逐条删除，删完自动重新拉（删除后列表前移，重拉即拿到新的「最前面」），直到以下任一条件自动停止：

1. **删完** → 打印 `没有回帖了，全部删完`；
2. **命中风控** → 打印 `⚠️ 检测到「操作频繁/风控」，已自动停止`，并提示等待时间；
3. **检测到 `stop.txt`** → 在项目目录放一个空文件 `stop.txt`，或按 `Ctrl+C`，随时手动停。

删除接口返回里出现「频繁 / 太快 / 限制 / 风控 / 稍后」等关键词即判定为风控。**真撞上风控时，把终端打印的 `删除失败 pid=xxx，err=???` 贴出来，即可把判定精确化。**

因为始终删的是「最前面的回贴」，所以中断后再跑，会自然接着剩下的继续，无需记录进度。

### 为什么快

UI 版的时间几乎全耗在「找元素 → 等元素出现 → 点按钮 → 等页面渲染」上；接口版把这一整层 DOM 交互都绕过了，只剩**网络往返 + 人为加的随机延时**（随机延时是为风控留的缓冲，不是白等）。

---

## 快速开始

1. **装 uv**（Python 包管理器，负责环境与依赖）：
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
2. **装依赖**（项目目录下）：
   ```powershell
   uv sync
   ```
3. **启动调试版 Edge 并登录**：双击 `start_edge.bat`，在弹出的独立窗口里打开 `tieba.baidu.com` 登录，保持窗口开着。
4. **改地址**：编辑 `fast_mode.py` 顶部 `TIEBA_URL`，换成你自己的主页地址。
5. **跑**：
   ```powershell
   uv run fast_mode.py --list-only   # 先数一下还有多少条
   uv run fast_mode.py               # 开始删
   ```

### 拿 TIEBA_URL

登录贴吧 → 点自己头像进个人主页 → 点「回贴」tab → 复制地址栏完整网址。形如：

```
https://tieba.baidu.com/home/main?id=你的贴吧ID&fr=personalize_page
```

其中 `id=xxx` 那串就是你的贴吧 ID，替换进 `TIEBA_URL` 即可。

### 调试版 Edge 的原理

脚本通过 Edge 的远程调试端口（默认 9222）附着到「你已经登录的窗口」。启动命令里两个参数缺一不可：

- `--remote-debugging-port=9222`：开调试端口，端口与 `DEBUG_ADDRESS` 一致；
- `--user-data-dir=C:\selenium_edge_profile`：独立配置目录（新版 Edge 禁止在默认目录开调试；独立目录也不影响你日常的浏览器）。

驱动方面：Selenium 4 内置 Selenium Manager，首次运行自动下载匹配版本的 `msedgedriver`，一般无需手动装。

---

## 配置

`fast_mode.py` 顶部：

| 变量 | 说明 |
|---|---|
| `TIEBA_URL` | 你的贴吧主页地址（**必改**） |
| `DEBUG_ADDRESS` | Edge 调试端口，默认 `127.0.0.1:9222` |
| `BATCH_SIZE` | 连续模式每轮拉取条数，默认 20 |
| `DELETE_WAIT` | 删除后随机等待秒数，默认 `(2, 4)`；太小易触发风控 |
| `NORMAL_WAIT` | 翻页随机等待秒数 |
| `SIGN_SECRET` | 接口签名密钥，接口失效时重点排查这里 |
| `RATE_LIMIT_KEYWORDS` | 风控判定关键词列表 |

---

## main.py（UI 自动化版）

在浏览器页面上模拟点击删除，走「删第一条 → 刷新 → 继续」的循环，含自动滚动预加载、二次刷新兜底。速度慢，但**不依赖接口签名**——当接口版因签名失效跑不动时，用它兜底。配置同样在文件顶部。

---

## 常见问题

**连不上浏览器（`DevToolsActivePort` 相关）？**
用 `start_edge.bat` 启动，确认端口与 `DEBUG_ADDRESS` 都是 9222。

**删到一半停了？**
大概率命中风控，看终端提示，等一段时间（几十分钟到几小时）再跑。

**报 `SessionNotCreatedException`？**
驱动版本与 Edge 版本不匹配，手动下载对应版本的 `msedgedriver` 放到项目目录。

---

## 免责声明

本工具仅用于删除你自己账号的内容。请遵守百度贴吧用户协议及相关法律法规。批量操作可能触发平台风控，请适度使用、放慢节奏。由此产生的一切后果由使用者自行承担。
