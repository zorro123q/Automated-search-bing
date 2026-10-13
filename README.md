# Automated Search Bing

**基于 Playwright + Microsoft Edge 的 Bing 自动搜索工具**

一个轻量级的 Python 浏览器自动化项目，通过 Playwright 调用本机 Microsoft Edge，实现多轮中英文混合搜索、关键词去重、搜索结果浏览与独立登录会话管理。

无需下载或配置 `msedgedriver.exe`，直接使用系统已安装的 Microsoft Edge。

## ✨ 功能特性

| 功能 | 说明 |
|---|---|
| 🌐 中英混合搜索 | 支持中文、英文以及中英文组合搜索 |
| 🎲 随机搜索内容 | 支持关键词、短语、陈述句、疑问句等多种表达方式 |
| 📚 多领域搜索 | 从不同主题分类中选取内容，减少重复 |
| 🔄 历史去重 | 自动保存搜索历史，避免跨运行重复 |
| 🔍 搜索结果浏览 | 随机选择前 N 条普通搜索结果进行访问 |
| 📖 页面浏览 | 在结果页面随机停留、滚动阅读 |
| 🖥️ 可视化运行 | 使用本机 Edge 显示完整浏览器操作过程 |
| 🔐 登录状态保持 | 通过独立浏览器 Profile 保存登录会话 |
| 🚀 直接搜索 | 直接访问 Bing 搜索结果页面，减少首页交互 |
| 🛠️ 调试支持 | 支持在出现异常时保存页面截图，便于排查 |

## 📋 环境要求

运行前请确保具备以下环境：

- Windows 10 / Windows 11
- Microsoft Edge 浏览器
- Python 3.9 或更新版本（具体以安装的 Playwright 版本要求为准）
- 可正常访问 Bing 的网络连接

**技术栈**

- Python
- Playwright
- Microsoft Edge（Chromium）

本项目采用 Playwright 的浏览器控制能力，不依赖 Selenium 或 Edge WebDriver。

## 📦 安装与配置

### 1. 获取项目

使用 Git 克隆仓库：

    git clone https://github.com/<username>/Automated-search-bing.git
    cd Automated-search-bing

也可以直接从 GitHub 下载项目 ZIP 文件并解压。

### 2. 安装依赖

在终端执行：

    python -m pip install -U playwright

本项目使用系统已安装的 Edge，通过 `channel="msedge"` 启动，因此通常无需额外下载 Playwright Chromium 浏览器。

### 3. 首次运行

执行：

    python search_engine.py

如果实际脚本文件名不同，请替换为对应的 Python 文件名。

## 🔑 首次登录 Bing

为了保留 Microsoft / Bing 账号登录状态，建议首次运行时手动登录。

**步骤一：开启登录暂停**

在脚本配置区域找到：

    PAUSE_FOR_LOGIN = True

**步骤二：运行脚本**

    python search_engine.py

**步骤三：登录账号**

1. 等待程序打开 Microsoft Edge。
2. 在弹出的浏览器中登录 Microsoft / Bing 账号。
3. 登录完成后，返回终端。
4. 按下 Enter，继续执行搜索任务。

**步骤四：关闭登录暂停**

首次登录成功后，可以将配置修改为：

    PAUSE_FOR_LOGIN = False

后续运行将尝试复用保存在 `edge_automation_profile/` 中的登录状态。

> 注意：自动化浏览器采用独立 Profile，不会直接继承日常 Edge 浏览器中的账号登录状态。Cookie 过期、账号安全验证或会话失效后，可能需要重新登录。

## ⚙️ 配置说明

所有主要运行参数均可在脚本顶部调整。

| 参数 | 示例值 | 说明 |
|---|---|---|
| `SEARCH_COUNT` | `10` | 每次运行执行的搜索轮数 |
| `HEADLESS` | `False` | 是否启用无头模式 |
| `CLICK_RESULT` | `True` | 是否访问搜索结果网页 |
| `TOP_RESULT_COUNT` | `3` | 从前 N 条有效结果中随机选择 |
| `MIN_WAIT` | `10` | 两轮搜索之间的最短等待时间（秒） |
| `MAX_WAIT` | `30` | 两轮搜索之间的最长等待时间（秒） |
| `MIN_BROWSE` | `30` | 结果网页的最短浏览时间（秒） |
| `MAX_BROWSE` | `60` | 结果网页的最长浏览时间（秒） |
| `BING_URL` | `https://cn.bing.com` | Bing 搜索服务地址 |
| `PAUSE_FOR_LOGIN` | `False` | 是否在启动时等待手动登录 |

其中 `PAUSE_FOR_LOGIN` 建议首次登录时设为 `True`，常规运行时设为 `False`。

### 常用配置

**仅执行搜索，不访问结果网页**

    CLICK_RESULT = False

**执行 20 轮搜索**

    SEARCH_COUNT = 20

**设置结果浏览时间为 30～60 秒**

    MIN_BROWSE = 30
    MAX_BROWSE = 60

**切换 Bing 搜索地址**

    BING_URL = "https://www.bing.com"

## 🚀 运行流程

执行：

    python search_engine.py

程序将依次执行以下步骤：

1. **加载历史记录**：读取此前使用的搜索词与主题分类。
2. **生成搜索内容**：从不同主题中生成中文、英文或中英混合搜索词。
3. **检查重复**：根据历史记录过滤已经使用的内容。
4. **打开搜索页面**：使用 Edge 直接访问 Bing 搜索结果页。
5. **选择搜索结果**：如果启用了结果点击，从前 N 条有效普通结果中随机选择。
6. **浏览目标网页**：在设定时间内停留并执行随机滚动。
7. **保存搜索历史**：将本轮搜索内容写入本地历史记录。
8. **进入下一轮**：等待随机时间后重复，直至完成指定轮数。

实际执行顺序和异常处理细节以脚本实现为准。

## 📁 项目文件说明

典型的运行目录如下：

    Automated-search-bing/
    ├── search_engine.py
    ├── README.md
    ├── search_keyword_history.json
    ├── edge_automation_profile/
    └── bing_debug_*.png

| 文件或目录 | 用途 |
|---|---|
| `search_engine.py` | 自动搜索主程序 |
| `README.md` | 项目使用说明 |
| `search_keyword_history.json` | 保存搜索词与历史主题，用于去重 |
| `edge_automation_profile/` | 保存 Edge 独立浏览器会话、Cookie 等数据 |
| `bing_debug_*.png` | 出现异常时生成的调试截图 |

历史记录文件、调试截图和浏览器 Profile 可能在首次运行后才创建。

### 推荐的 .gitignore

为了避免上传个人浏览器数据和运行时文件，建议在 `.gitignore` 中加入：

    # Browser profile
    edge_automation_profile/

    # Search history
    search_keyword_history.json

    # Debug screenshots
    bing_debug_*.png

    # Python cache
    __pycache__/
    *.py[cod]

    # Virtual environments
    .venv/
    venv/

    # Environment files
    .env
    .env.*

特别注意：`edge_automation_profile/` 可能包含账号 Cookie、登录会话及浏览器缓存，不应上传到公共 GitHub 仓库。

## ❓ 常见问题

### Q1：需要安装 msedgedriver.exe 吗？

不需要。

项目使用 Playwright，通过 `channel="msedge"` 调用本机 Edge 浏览器，而不是使用 Selenium WebDriver。

### Q2：为什么自动化 Edge 没有登录我的 Microsoft 账号？

这是因为脚本使用独立浏览器 Profile，与日常使用的 Edge Profile 不同。

首次运行需要手动登录，登录信息将保存在本地独立 Profile 目录中。

如果会话过期，可能需要再次登录。

### Q3：为什么 Edge 顶部显示“正由自动测试软件控制”？

这是浏览器检测到自动化控制后显示的正常提示。

它不一定代表网站已经限制访问，也不意味着搜索一定失败。

部分网站可能会识别自动化浏览器并限制访问，此时应遵守网站的访问规则，不应依赖隐藏自动化标志来绕过限制。

### Q4：为什么自动化打开的网页显示不完整？

可能与以下因素有关：

- 浏览器窗口大小与页面视口尺寸不一致
- 页面采用响应式布局
- Windows 显示缩放比例影响布局
- 浏览器尚未完成页面加载
- 网站存在自动化环境兼容性问题

建议首先检查浏览器窗口尺寸与 Playwright 的 `viewport` 配置，并结合调试截图确认具体原因。

### Q5：是否需要添加 --no-sandbox？

通常不需要。

`--no-sandbox` 会降低浏览器进程的安全隔离能力，并可能触发浏览器安全警告。

本项目建议优先使用 Edge 的正常安全配置运行。

### Q6：为什么搜索词有时都是疑问句？

搜索词的表达形式取决于脚本中的生成策略及语料库。

可以在关键词生成逻辑中调整不同类型的比例，例如关键词、短语、陈述句和疑问句，以提高内容多样性。

### Q7：如何清除搜索历史？

关闭脚本后，删除：

    search_keyword_history.json

下次运行将重新建立搜索历史记录。

### Q8：如何重新登录账号？

将：

    PAUSE_FOR_LOGIN = True

重新运行脚本后，在 Edge 中手动完成登录。

如果需要重置整个独立浏览器环境，可在关闭所有使用该 Profile 的浏览器进程后删除 `edge_automation_profile/`。此操作将同时清除其中保存的登录会话等数据。

## ⚠️ 使用说明

1. 本项目主要用于浏览器自动化学习、搜索流程测试和 Playwright 技术研究。
2. 不包含自动绕过验证码、人机验证或网站访问限制的功能。
3. 请合理控制运行频率，避免对搜索服务或目标网站造成不必要的请求负担。
4. 请遵守 Microsoft Bing 及目标网站的服务条款。
5. 项目不保证搜索结果位置、网页结构或账号状态长期保持不变。
6. 浏览器自动化可能受网络状态、Edge 更新及网站页面变化影响。

## 📚 相关资料

- [Playwright Python 官方文档](https://playwright.dev/python/)
- [Playwright 浏览器管理](https://playwright.dev/python/docs/browsers)
- [Microsoft Edge 官方网站](https://www.microsoft.com/edge)

## 📄 免责声明

本项目仅供学习、技术研究及合规的自动化测试用途。

使用者应自行确保相关操作符合目标平台的服务条款及适用法律法规。项目不提供绕过反自动化检测、验证码或访问限制的能力。

---

**Automated Search Bing — 使用 Python + Playwright 实现轻量级 Bing 浏览器自动化。**
