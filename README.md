# Automated-search-bing

# Bing 中英混合自动搜索脚本（Playwright + 本机 Edge）

使用 Playwright 控制本机 Microsoft Edge，自动完成多轮中英混合随机搜索。  
**无需下载 msedgedriver.exe**，直接调用系统已安装的 Edge。

---

## 功能特性

- **中英混合搜索句**：支持关键词、短语、陈述句、中英混合、提问等多种风格
- **领域去重**：每轮从不同主题分类中选取，避免内容高度重复
- **历史记录**：自动记录已用主题与搜索词，跨运行去重
- **结果点击浏览**：随机选择前 3 条普通结果之一进入网页
- **模拟阅读**：进入结果页后停留 30～60 秒，并随机滚动
- **窗口最大化**：启动后自动最大化 Edge 窗口
- **独立登录会话**：使用本地 Profile 目录保存登录状态，下次无需重新登录
- **直接打开搜索结果页**：跳过 Bing 首页，避免搜索建议弹窗干扰

---

## 环境要求

- Windows（推荐）
- 已安装 Microsoft Edge
- Python 3.8+

---

## 安装

```bash
python -m pip install -U playwright
```

安装完成后，Playwright 会自动使用系统中的 Edge（通过 `channel="msedge"`）。

---

## 首次使用（登录）

1. 打开脚本，将顶部配置改为：

```python
PAUSE_FOR_LOGIN = True
```

2. 运行脚本：

```bash
python your_script_name.py
```

3. 弹出的 Edge 窗口中，手动登录你的 Microsoft / Bing 账号。
4. 登录完成后，回到终端按 **Enter**，脚本开始执行搜索。
5. 登录成功后，将配置改回：

```python
PAUSE_FOR_LOGIN = False
```

之后运行会自动复用 `edge_automation_profile` 目录中的登录状态。

---

## 配置说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `SEARCH_COUNT` | `10` | 搜索轮数 |
| `HEADLESS` | `False` | 是否无头模式（建议保持 False） |
| `CLICK_RESULT` | `True` | 是否点击搜索结果并进入网页阅读 |
| `TOP_RESULT_COUNT` | `3` | 从前 N 条结果中随机选择 |
| `MIN_WAIT` / `MAX_WAIT` | `10` / `30` | 每轮搜索之间的等待时间（秒） |
| `MIN_BROWSE` / `MAX_BROWSE` | `30` / `60` | 进入结果页后的阅读时间（秒） |
| `BING_URL` | `https://cn.bing.com` | Bing 地址（可改为 `https://www.bing.com`） |
| `PAUSE_FOR_LOGIN` | `True` | 是否在启动时暂停等待手动登录 |

---

## 运行

```bash
python your_script_name.py
```

运行过程中会：

1. 生成不重复的中英混合搜索词
2. 直接打开 Bing 搜索结果页
3. 随机点击前 3 条结果之一
4. 在目标网页停留并滚动阅读 30～60 秒
5. 返回 Bing，等待一段时间后进入下一轮

---

## 文件说明

| 文件/目录 | 说明 |
|-----------|------|
| `search_keyword_history.json` | 历史搜索词与主题记录（用于去重） |
| `edge_automation_profile/` | 独立浏览器用户数据目录（保存登录状态） |
| `bing_debug_*.png` | 出错时自动保存的调试截图 |

> **注意**：`edge_automation_profile` 目录包含登录信息，请勿上传到公开仓库。

---

## 注意事项

- 本脚本**不包含**任何绕过验证码或人机验证的逻辑。如遇验证码、访问限制等，请人工处理。
- 建议关闭无头模式（`HEADLESS = False`），真实窗口更接近正常使用行为。
- 独立 Profile 不会自动继承你日常使用的 Edge 登录状态，首次需手动登录一次。
- 仅供个人学习与自动化测试使用，请遵守相关服务条款。

---

## 依赖

- [Playwright](https://playwright.dev/python/)（Python 版）
```
