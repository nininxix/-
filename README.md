# 贴吧回贴批量删除工具

一键批量删除你在百度贴吧里发过的所有「回贴」。

> ⚠️ 只删**你自己账号**的回贴。请勿用于删除他人内容或任何违规用途。

---

## 目录

1. [这是什么（项目介绍）](#这是什么项目介绍)
2. [功能特性](#功能特性)
3. [它是怎么工作的](#它是怎么工作的)
4. [环境要求](#环境要求)
5. [快速开始（新手一步步实操）](#快速开始新手一步步实操)
6. [需要修改的地方（重要）](#需要修改的地方重要)
7. [Edge 浏览器与驱动下载](#edge-浏览器与驱动下载)
8. [Selenium 连接技巧详解（盘外招）](#selenium-连接技巧详解盘外招)
9. [uv 使用教程](#uv-使用教程)
10. [安全措施](#安全措施)
11. [文件说明](#文件说明)
12. [常见问题（FAQ）](#常见问题faq)
13. [免责声明](#免责声明)

---

## 这是什么（项目介绍）

百度贴吧没有提供「一键清空回贴」的功能。想删掉以前发过的大量回贴，只能一条一条手动点「… → 删除 → 确定」，几百上千条会点到怀疑人生。

这个工具用 **Selenium** 控制一个**已经手动登录好的 Edge 浏览器**，自动帮你重复执行：

> 删第一条 → 等刷新 → 删下一条 → … → 列表删空了就 `刷新页面` 重新加载 → 继续删 → 直到全部删完。

它最大的特点是**不需要把账号密码写进代码**：登录完全由你自己在浏览器里手动完成，程序只是「借」你那个已经登录的窗口来操作。

---

## 功能特性

- ✅ **不碰密码**：连接已登录浏览器，代码里没有任何账号密码。
- ✅ **自动刷新续删**：删到当前页面空了，自动 `refresh()` 重新加载，避免「空白页导致脚本提前结束、帖子却没删完」的问题。
- ✅ **刷新后主动预加载**：刷新后自动滚动列表（含内部容器）加载更多，攒够约 10 条再删；首批太少还会二次刷新，避免反复刷新。
- ✅ **紧急停止**：随时放一个 `stop.txt` 文件就能让它停下来。
- ✅ **二次确认**：启动时要求输入 `YES` 才真正开始，防止误触。
- ✅ **最大数量限制**：默认最多删 500 条就自动停，防止跑飞。
- ✅ **出错自动截图**：删除失败会把当前页面截图存到 `screenshots/`，方便排查。
- ✅ **随机延时**：模拟人工节奏，降低触发风控的概率。

---

## 它是怎么工作的

```
启动调试版 Edge（开 9222 端口）
        ↓
    手动登录贴吧
        ↓
程序通过 debuggerAddress 连上这个 Edge
        ↓
打开个人主页 → 切到「回贴」tab
        ↓
    ┌─ 删除第一条回贴 ─┐
    │        ↓        │
    │   列表还有吗？   │
    │   有 → 继续删    │
    │   空 → refresh   │
    │        ↓        │
    └── 重新加载再删 ──┘
        ↓
   全部删完 / 达到上限 / 发现 stop.txt → 结束
```

---

## 环境要求

| 项目 | 要求 |
|------|------|
| 系统 | Windows 10 / 11（本文档按 Windows 写） |
| 浏览器 | Microsoft Edge（平时用的那个就行） |
| 包管理器 | uv（负责建虚拟环境、装依赖、管 Python 版本） |
| Python | 不需要手动装，uv 会自动下载 |

---

## 快速开始（新手一步步实操）

总共 4 步：**装 uv → 装依赖 → 启动调试版 Edge 并登录 → 改地址 → 跑脚本**。

### 第 0 步：下载本项目

```bash
git clone git@github.com:nininxix/baidu-tieba-delete-script.git
cd baidu-tieba-delete-script
```

> 克隆下来后进入 `baidu-tieba-delete-script` 目录即可。

### 第 1 步：安装 uv（没装的话）

在 PowerShell 里执行：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

验证：

```powershell
uv --version
```

> 已经装过就跳过这步。

### 第 2 步：建虚拟环境 + 装依赖

在项目目录下执行：

```powershell
uv sync
```

`uv` 会自动创建 `.venv` 虚拟环境，并下载安装 `selenium`。

### 第 3 步：启动「调试版」Edge 并登录贴吧

**这一步最关键，别用你日常的浏览器窗口。**

双击项目里的 `start_edge.bat`（或者 PowerShell 里跑 `.\start_edge.ps1`）。

它会启动一个**独立的、带调试端口的 Edge 窗口**。在弹出的这个窗口里：

1. 打开 `tieba.baidu.com`，**手动登录**你的账号；
2. 登录后**保持这个窗口开着**，不要关。

### 第 4 步：改地址 + 运行

1. 用记事本打开 `main.py`，找到 `TIEBA_URL` 这一行，把它改成你自己的贴吧主页地址（怎么找看下一节）。
2. 回到 PowerShell，在项目目录执行：

```powershell
uv run main.py
```

3. 屏幕会提示「输入 YES 开始」，输入大写 `YES` 回车，就开始自动删了。

中途想停，两种方式任选：
- 在项目目录新建一个空文件 `stop.txt`（脚本会自动检测并停止）；
- 或按 `Ctrl + C`。

---

## 需要修改的地方（重要）

打开 `main.py`，最上面的「配置区域」就是所有需要动的地方：

| 变量 | 说明 | 是否必改 |
|------|------|----------|
| `TIEBA_URL` | 你的贴吧个人主页地址 | ✅ **必改** |
| `DEBUG_ADDRESS` | 调试端口，一般不用改 | 一般不用 |
| `MAX_DELETE_COUNT` | 最大删除条数（默认 500） | 按需 |
| `MIN_BATCH_SIZE` | 预加载攒够多少条再删（默认 10） | 按需 |
| `MAX_LOAD_ROUND` | 预加载最多滚动几轮（默认 5） | 按需 |
| `EMPTY_LIMIT` | 连续几次空页面就刷新（默认 2） | 按需 |
| `DELETE_WAIT` / `NORMAL_WAIT` | 删除后 / 普通随机等待（秒） | 按需 |

### 怎么拿到你自己的 `TIEBA_URL`

1. 在登录好的贴吧里，点自己的头像进入「个人主页」；
2. 点页面上的「回贴」tab；
3. 复制浏览器**地址栏里的完整网址**（形如 `https://tieba.baidu.com/home/main?id=xxxxx&fr=personalize_page`）；
4. 把 `main.py` 里的 `TIEBA_URL = "你的贴吧主页URL"` 整段替换成你复制的网址。

> 那串 `id=xxxxx` 就是你的贴吧 ID，每个人的都不一样，所以必须换成自己的。

---

## Edge 浏览器与驱动下载

### Edge 浏览器

Windows 一般自带 Edge，不用额外下载。如果实在没有，去微软官网下载安装即可：
<https://www.microsoft.com/edge>

### Edge 驱动（msedgedriver）

**好消息：本项目用 Selenium 4，驱动是自动管理的，绝大多数情况你不需要手动下载。**

Selenium 4 内置了 **Selenium Manager**，第一次运行时会自动检测你 Edge 的版本，并下载对应的 `msedgedriver`，放到缓存目录里。所以：

> ✅ 正常情况：什么都不用做，直接 `uv run main.py` 即可。

### 什么时候需要手动下载驱动？

只有当自动下载失败时（比如网络访问不了官方源），才需要手动：

1. 打开 Edge，地址栏输入 `edge://version`，记下「Microsoft Edge」的版本号（比如 `126.0.2592.61`）；
2. 去微软官方驱动下载页，下载**和你的版本号完全对应**的 `msedgedriver`：
   <https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/>
3. 解压后得到一个 `msedgedriver.exe`，把它放到**项目目录里**（和 `main.py` 同一个文件夹），或者放到系统 `PATH` 里的某个目录（比如 `C:\Windows\System32`）。

> 版本号必须一致，否则会报「SessionNotCreatedException: session not created」之类的错。

---

## Selenium 连接技巧详解（盘外招）

这段是「为什么会这样设计」的原理说明，理解了遇到问题才好排查。

### 1. 为什么「连接已登录浏览器」而不是自己输密码？

如果让 Selenium 自己打开浏览器再登录，会面临：验证码、短信验证、扫码、风控拦截等一堆麻烦，而且你得把密码写进代码（不安全）。

**盘外招**：让 Edge 开一个「远程调试端口」，Selenium 通过 `debuggerAddress` 直接**附着**到你那个已经登录的窗口上，相当于「接管」这个窗口，天然带着你的登录状态，跳过所有登录验证。

代码里就这两句：

```python
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Edge(options=options)
```

### 2. 为什么启动 Edge 必须带 `--user-data-dir`？

启动命令长这样：

```
msedge.exe --remote-debugging-port=9222 --user-data-dir=C:\selenium_edge_profile
```

两个参数缺一不可：

- `--remote-debugging-port=9222`：开一个调试端口，Selenium 靠它连进来。端口号要和 `main.py` 里的 `DEBUG_ADDRESS` 一致。
- `--user-data-dir=xxx`：指定一个**独立的配置目录**。新版 Edge 出于安全，**禁止在默认配置目录上开远程调试**；而且用独立目录也不影响你日常用的 Edge（互不干扰）。

> `C:\selenium_edge_profile` 这个目录可以随便换，只要是空目录或专用目录即可。换的话 `start_edge.bat` 和 `start_edge.ps1` 里一起改。

### 3. Edge 的安装路径在哪？

`start_edge.bat` 里写的是：

```
C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
```

如果你的电脑上这个路径不存在，Edge 可能装在另一个位置，常见的有：

```
C:\Program Files\Microsoft\Edge\Application\msedge.exe
```

可以在文件资源管理器里确认一下，把 `start_edge.bat` 里的路径改成实际存在的那个。

### 4. 为什么用 `execute_script` 去点击，而不是 `.click()`？

有些按钮被遮挡、或者不是「标准可点」状态，直接 `.click()` 会报 `element not clickable`。用 JS 强制点击可以绕过：

```python
driver.execute_script("arguments[0].click();", element)
```

### 5. 为什么要先 `move_to_element` 再点「三个点」？

贴吧的「…」菜单是**悬停（hover）**才弹出的，所以先鼠标移过去，等菜单出现，再点。

```python
ActionChains(driver).move_to_element(more).perform()
```

### 6. 为什么用 `driver.refresh()` 而不是往下滚动加载？

删到当前页面空了之后，最省事、最稳的做法就是**刷新整个页面重新加载**。这样能保证「空白页不会导致脚本误以为删完了就提前结束」，这正是这版代码的核心改进点。

---

## uv 使用教程

`uv` 是一个很快的 Python 包管理器。下面是本项目会用到的命令。

### 常用命令

| 命令 | 作用 |
|------|------|
| `uv sync` | 按 `pyproject.toml` 建/更新虚拟环境并装依赖 |
| `uv run main.py` | 用项目虚拟环境运行脚本 |
| `uv add <包名>` | 添加依赖（自动写入 pyproject.toml） |
| `uv remove <包名>` | 移除依赖 |
| `uv run python -c "import selenium; print(selenium.__version__)"` | 检查 selenium 版本 |
| `uv python list` | 查看可用的 Python 版本 |

### 不用「激活」环境

`uv run` 会自动用项目 `.venv` 里的 Python 跑脚本，**不需要**手动 `activate`，比传统的 `venv` 省事很多。

### 上传「轻量版」给别人

上传时**不要**传 `.venv`（很大，且和环境绑定）。只需传：

- `main.py`
- `pyproject.toml`
- `README.md`
- `start_edge.bat` / `start_edge.ps1`

别人拿到后一句 `uv sync` + `uv run main.py` 就能复现环境。

---

## 安全措施

| 措施 | 说明 |
|------|------|
| 二次确认 | 启动后必须输入大写 `YES` 才开始，防止误触 |
| 最大删除数量 | `MAX_DELETE_COUNT = 500`，删够就停 |
| 紧急停止 | 在项目目录放一个空文件 `stop.txt`，脚本检测到就停 |
| Ctrl+C | 终端里按 `Ctrl+C` 也能停 |
| 错误截图 | 删除异常时自动截图到 `screenshots/` |

---

## 文件说明

```
.
├── main.py             # 主程序（UI 自动化版，配置都在文件顶部）
├── fast_mode.py        # 接口加速版（实验性，连浏览器后直接调接口）
├── pyproject.toml      # uv 项目配置，声明依赖 selenium
├── start_edge.bat      # 双击启动「调试版 Edge」（Windows 双击友好）
├── start_edge.ps1      # 同上，PowerShell 版
├── README.md           # 本说明文档
├── .gitignore          # git 忽略规则
└── .venv/              # 虚拟环境（uv sync 生成，不上传）
```

---

## 常见问题（FAQ）

**Q1：报 `DevToolsActivePort` 相关错误，连不上浏览器？**
大概率是启动 Edge 时没带 `--user-data-dir`，或端口对不上。用 `start_edge.bat` 启动，并确认端口和 `main.py` 里的 `DEBUG_ADDRESS` 都是 `9222`。

**Q2：连上了，但找不到「回贴」tab 或删除按钮？**
贴吧页面改版了，页面元素定位失效。参考下一节「定位失效怎么办」。

**Q3：报 `SessionNotCreatedException: session not created`？**
驱动版本和 Edge 版本不匹配。看上文「Edge 浏览器与驱动下载」一节，手动下载对应版本的 `msedgedriver`。

**Q4：会误删别人、或者删错吗？**
不会。它只在你自己的「回贴」列表里操作。

**Q5：会不会被风控 / 封号？**
脚本加了随机延时、放慢节奏，但批量操作任何账号都有一定风险，请自行评估，不要调太快。

**Q6：`TIEBA_URL` 忘了改会怎样？**
会打开一个无效页面。脚本第一步就是读这个地址，所以运行前务必改成自己的。

### 定位失效怎么办（进阶）

贴吧前端经常改版，导致脚本里的 XPath / CSS 选择器失效。重新抓一遍：

1. 在登录好的 Edge 里按 `F12` 打开开发者工具；
2. 点左上角「选择元素」图标（一个箭头），点页面上的一条回复；
3. 在 `Elements` 面板里，右键对应元素 → `Copy` → `Copy XPath`（或 `Copy selector`）；
4. 把结果填回 `main.py` 对应位置。

一般要重新抓的是 `get_replies` 里的 `REPLY_LIST_XPATH`，以及 `.thread-setting`、删除/确定按钮的定位。

---

## 免责声明

本工具仅用于**删除你自己账号下的回贴**。请遵守百度贴吧用户协议及相关法律法规。使用本工具产生的任何后果由使用者自行承担。

- 批量操作可能触发平台频率限制或风控，请适度使用、放慢节奏；
- 请勿用于删除他人内容、批量操作他人账号等任何违规行为。
