import json
import random
import re
import time
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from playwright.sync_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeout,
    sync_playwright,
)


# ========== 基础配置 ==========
SEARCH_COUNT = 10
HEADLESS = False
CLICK_RESULT = True
TOP_RESULT_COUNT = 3
MIN_WAIT, MAX_WAIT = 10, 30
MIN_BROWSE, MAX_BROWSE = 30, 60
MIN_SCROLL, MAX_SCROLL = 1, 3
PAGE_TIMEOUT = 60000  # 毫秒
LOAD_TIMEOUT = 45000  # 网页静态资源加载最长等待（毫秒）
PAUSE_FOR_LOGIN = True  # 首次手动登录时改 True，登录完成后按 Enter 再开始搜索
# 截图里日常使用的是 cn.bing.com；若想使用国际版，可换成 https://www.bing.com
BING_URL = "https://cn.bing.com"
RESULT_SELECTOR = "#b_results .b_algo h2 a[href]:visible"
SCRIPT_DIR = Path(__file__).resolve().parent
HISTORY_FILE = SCRIPT_DIR / "search_keyword_history.json"
PROFILE_DIR = SCRIPT_DIR / "edge_automation_profile"  # 独立目录，请不要上传 GitHub


# 不同分类下是不同的搜索主题，避免单轮集中在相似内容上。
TOPIC_CATEGORIES = {
    "科技与AI": [
        ("人工智能", "artificial intelligence"),
        ("机器人", "robotics"),
        ("智能家居", "smart home"),
        ("计算机视觉", "computer vision"),
    ],
    "软件与开发": [
        ("Python 编程", "Python programming"),
        ("网页开发", "web development"),
        ("数据库设计", "database design"),
        ("自动化测试", "automated testing"),
    ],
    "数码设备": [
        ("智能手机", "smartphone"),
        ("笔记本电脑", "laptops"),
        ("数码相机", "digital camera"),
        ("电脑硬件", "computer hardware"),
    ],
    "旅行与地理": [
        ("日本旅行", "Japan travel"),
        ("欧洲城市", "European cities"),
        ("世界地理", "world geography"),
        ("自然景观", "natural landscapes"),
    ],
    "科学与宇宙": [
        ("天文学", "astronomy"),
        ("海洋科学", "marine science"),
        ("物理实验", "physics experiments"),
        ("太空探索", "space exploration"),
    ],
    "历史与文化": [
        ("古代文明", "ancient civilizations"),
        ("世界历史", "world history"),
        ("传统文化", "traditional culture"),
        ("博物馆", "museums"),
    ],
    "语言与教育": [
        ("英语学习", "learning English"),
        ("日语学习", "learning Japanese"),
        ("在线课程", "online courses"),
        ("学习方法", "study methods"),
    ],
    "影视与音乐": [
        ("电影赏析", "film analysis"),
        ("音乐类型", "music genres"),
        ("电影配乐", "film soundtracks"),
        ("动画电影", "animated films"),
    ],
    "体育与运动": [
        ("足球比赛", "football matches"),
        ("健身训练", "fitness training"),
        ("篮球技巧", "basketball skills"),
        ("户外徒步", "hiking"),
    ],
    "自然与生态": [
        ("野生动物", "wildlife"),
        ("鸟类观察", "birdwatching"),
        ("生态保护", "conservation"),
        ("植物科普", "botany"),
    ],
    "美食与烹饪": [
        ("家常菜", "home cooking"),
        ("烘焙技巧", "baking tips"),
        ("咖啡制作", "coffee brewing"),
        ("地方美食", "local cuisine"),
    ],
    "摄影与设计": [
        ("摄影构图", "photo composition"),
        ("平面设计", "graphic design"),
        ("建筑摄影", "architecture photography"),
        ("室内设计", "interior design"),
    ],
    "经济与商业": [
        ("市场营销", "marketing"),
        ("创业案例", "startup case studies"),
        ("商业模式", "business models"),
        ("电子商务", "ecommerce"),
    ],
    "交通与工程": [
        ("电动汽车", "electric cars"),
        ("高铁技术", "high speed rail"),
        ("航空知识", "aviation"),
        ("城市交通", "urban transport"),
    ],
    "日常生活": [
        ("时间管理", "time management"),
        ("家庭收纳", "home organization"),
        ("宠物护理", "pet care"),
        ("园艺入门", "gardening"),
    ],
}

# 为每个主题指定语义相关的搜索角度，避免“时间管理的省钱技巧”之类的错配。
TOPIC_DETAILS = {
    "人工智能": ["生活中的应用", "AI 助手实践", "就业影响", "最新发展"],
    "机器人": ["家庭服务机器人", "工业机器人应用", "机器人编程", "机器人发展趋势"],
    "智能家居": ["设备联动方案", "智能照明", "家庭安防", "新手设备清单"],
    "计算机视觉": ["目标检测案例", "图像识别算法", "开源项目", "工业应用"],
    "Python 编程": ["入门教程", "文件处理", "数据分析实战", "基础练习"],
    "网页开发": ["HTML CSS 基础", "响应式布局", "前端项目", "开发工具"],
    "数据库设计": ["表结构规范", "索引优化", "ER 图", "实战案例"],
    "自动化测试": ["Playwright 教程", "常见异常", "测试脚本示例", "测试框架对比"],
    "智能手机": ["拍照对比", "续航测评", "选购建议", "系统更新"],
    "笔记本电脑": ["性能选择", "轻薄本推荐", "电池续航", "硬件配置"],
    "数码相机": ["摄影入门", "镜头选择", "传感器尺寸", "画质对比"],
    "电脑硬件": ["显卡性能", "CPU 选购", "散热方案", "硬件兼容性"],
    "日本旅行": ["京都景点", "交通攻略", "秋季路线", "旅行预算"],
    "欧洲城市": ["城市建筑", "自由行路线", "当地交通", "历史街区"],
    "世界地理": ["世界地形", "气候分布", "地图学习", "有趣的地理现象"],
    "自然景观": ["国家公园", "地质奇观", "风景摄影", "旅行路线"],
    "天文学": ["星座观测", "行星知识", "望远镜入门", "最新发现"],
    "海洋科学": ["深海生物", "洋流原理", "海洋探索", "生态研究"],
    "物理实验": ["经典实验", "家庭小实验", "实验原理", "实验器材"],
    "太空探索": ["火星任务", "载人航天", "NASA 最新计划", "探测器技术"],
    "古代文明": ["文明起源", "重要遗址", "历史文献", "文化交流"],
    "世界历史": ["重要事件", "时间线", "历史地图", "代表人物"],
    "传统文化": ["非遗工艺", "传统节日", "民间艺术", "历史传承"],
    "博物馆": ["经典展品", "展览推荐", "参观指南", "文物修复"],
    "英语学习": ["口语练习", "词汇记忆", "听力训练", "日常表达"],
    "日语学习": ["五十音入门", "日语语法", "日常会话", "听力资源"],
    "在线课程": ["免费资源", "课程平台对比", "学习计划", "证书课程"],
    "学习方法": ["费曼学习法", "复习安排", "高效笔记", "专注力训练"],
    "电影赏析": ["镜头语言", "电影主题", "经典影片", "叙事结构"],
    "音乐类型": ["爵士乐特点", "电子音乐", "风格对比", "代表歌手"],
    "电影配乐": ["经典原声作品", "配乐创作过程", "作曲家介绍", "影视音乐分析"],
    "动画电影": ["经典作品", "动画制作", "故事设计", "艺术风格"],
    "足球比赛": ["战术分析", "球队阵型", "比赛规则", "经典赛事"],
    "健身训练": ["新手计划", "力量训练", "动作规范", "训练恢复"],
    "篮球技巧": ["投篮训练", "运球练习", "防守动作", "基础规则"],
    "户外徒步": ["线路选择", "登山装备", "安全准备", "路线规划"],
    "野生动物": ["动物习性", "野外摄影", "物种保护", "生态环境"],
    "鸟类观察": ["观鸟地点", "鸟类图鉴", "双筒望远镜", "迁徙季节"],
    "生态保护": ["湿地保护", "森林恢复", "生物多样性", "环保案例"],
    "植物科普": ["植物识别", "家庭植物", "叶片结构", "野生花卉"],
    "家常菜": ["快手食谱", "做饭步骤", "食材搭配", "厨房技巧"],
    "烘焙技巧": ["面包发酵", "蛋糕配方", "新手工具", "烘焙失败原因"],
    "咖啡制作": ["手冲教程", "磨豆粗细", "咖啡豆选择", "萃取技巧"],
    "地方美食": ["特色小吃", "经典菜系", "本地餐馆", "饮食文化"],
    "摄影构图": ["三分法", "引导线构图", "人像摄影", "风景构图"],
    "平面设计": ["版式设计", "字体搭配", "配色方法", "海报案例"],
    "建筑摄影": ["广角镜头", "建筑线条", "夜景拍摄", "构图技巧"],
    "室内设计": ["小户型布局", "照明设计", "空间收纳", "设计案例"],
    "市场营销": ["内容营销", "品牌定位", "用户增长", "推广案例"],
    "创业案例": ["小成本创业", "商业计划", "创业失败经验", "团队组建"],
    "商业模式": ["订阅制", "平台经济", "盈利方式", "企业案例"],
    "电子商务": ["电商运营", "选品方法", "用户体验", "物流管理"],
    "电动汽车": ["电池续航", "快充技术", "充电成本", "安全设计"],
    "高铁技术": ["列车运行原理", "轨道技术", "动力系统", "高速铁路发展"],
    "航空知识": ["飞机升力", "航线规划", "航空发动机", "民航科普"],
    "城市交通": ["公共交通规划", "自行车道", "交通拥堵", "地铁线路"],
    "时间管理": ["日程安排", "任务优先级", "专注力提升", "时间规划工具"],
    "家庭收纳": ["衣柜整理", "收纳用品", "厨房收纳", "小空间利用"],
    "宠物护理": ["日常喂养", "健康检查", "宠物行为", "新手养宠"],
    "园艺入门": ["阳台种植", "土壤选择", "植物浇水", "家庭园艺工具"],
}

# 搜索风格不是全部问句：关键词/短语/描述/中英混合/少量提问。
STYLE_WEIGHTS = {
    "keyword": 30,
    "phrase": 25,
    "statement": 20,
    "mixed": 15,
    "question": 10,
}

QUERY_TEMPLATES = {
    "keyword": [
        "{cn} {detail}",
        "{detail} {cn}",
        "{cn} {detail} 资料",
    ],
    "phrase": [
        "{cn}：{detail}",
        "{cn} / {detail}",
        "{cn} {detail} 入门资料",
    ],
    "statement": [
        "{cn}与{detail}相关的资料整理",
        "{cn}的{detail}专题介绍",
        "关于{cn}和{detail}的案例分享",
    ],
    "mixed": [
        "{cn} {en} {detail}",
        "{en} {cn} {detail}",
        "{detail} | {en} {cn}",
    ],
    "question": [
        "{cn}的{detail}有哪些实用建议？",
        "在哪里能找到关于{cn}的{detail}资料？",
        "如何查找{cn}的{detail}相关信息？",
    ],
}


def generate_style_plan(count):
    """风格组合随机但有保障：10 轮至少出现五种不同风格，问句最多约 20%。"""
    if count <= 0:
        return []
    styles = list(STYLE_WEIGHTS)
    plan = styles.copy() if count >= len(styles) else []
    question_limit = max(1, (count + 4) // 5)
    while len(plan) < count:
        available = [
            style for style in styles
            if style != "question" or plan.count("question") < question_limit
        ]
        plan.append(random.choices(
            available,
            weights=[STYLE_WEIGHTS[style] for style in available],
            k=1,
        )[0])
    random.shuffle(plan)
    return plan


def normalize_query(query):
    """仅用于去重：统一英文大小写，移除标点和空白。"""
    return re.sub(r"[^\w\u4e00-\u9fff]", "", query.casefold())


def load_history():
    """兼容旧版历史文件（仅 used_topics）与新版（含 used_queries）。"""
    if not HISTORY_FILE.exists():
        return {"used_topics": [], "used_queries": []}
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {
                "used_topics": [str(x) for x in data.get("used_topics", [])],
                "used_queries": [str(x) for x in data.get("used_queries", [])],
            }
    except (OSError, ValueError, TypeError) as exc:
        print(f"历史文件无法读取，将重新建立：{exc}")
    return {"used_topics": [], "used_queries": []}


def make_query(category, chinese, english, style, used_query_keys):
    """根据主题相关的内容和当前句式类型生成不重复搜索词。"""
    details = TOPIC_DETAILS.get(chinese, ["入门", "实用案例", "相关资料"])
    templates = QUERY_TEMPLATES[style]
    candidates = [
        template.format(cn=chinese, en=english, detail=detail)
        for detail in details for template in templates
    ]
    random.shuffle(candidates)
    for query in candidates:
        if normalize_query(query) not in used_query_keys:
            return query
    # 组合都用过时，不把历史无限增长视为真正能永远去重。
    return random.choice(candidates)


def generate_keywords(count):
    """按领域→具体主题→关注点→自然句式随机组合。"""
    categories = list(TOPIC_CATEGORIES)
    pool_size = sum(len(items) for items in TOPIC_CATEGORIES.values())
    if count > pool_size:
        raise ValueError(f"主题总数为 {pool_size}，最多只能选出 {pool_size} 个不同主题")

    history = load_history()
    old_topics = history["used_topics"]
    previously_used_topics = set(old_topics)
    recent_topics = set(old_topics[-min(30, len(old_topics)):])
    used_query_keys = {normalize_query(q) for q in history["used_queries"]}
    chosen_ids = set()

    # 十轮先选十个不同领域；超过领域数后允许多领域补齐。
    selected_categories = random.sample(categories, min(count, len(categories)))
    selected = []

    def select_topic(category):
        candidates = [
            (f"{category}|{cn}|{en}", category, cn, en)
            for cn, en in TOPIC_CATEGORIES[category]
            if f"{category}|{cn}|{en}" not in chosen_ids
        ]
        never_used = [x for x in candidates if x[0] not in previously_used_topics]
        not_recent = [x for x in candidates if x[0] not in recent_topics]
        choice = random.choice(never_used or not_recent or candidates)
        chosen_ids.add(choice[0])
        return choice

    for category in selected_categories:
        selected.append(select_topic(category))

    if len(selected) < count:
        extra_categories = categories[:]
        while len(selected) < count:
            possible = [
                c for c in extra_categories
                if any(f"{c}|{cn}|{en}" not in chosen_ids
                       for cn, en in TOPIC_CATEGORIES[c])
            ]
            if not possible:
                break
            selected.append(select_topic(random.choice(possible)))

    random.shuffle(selected)
    styles = generate_style_plan(count)
    result = []
    for (topic_id, category, cn, en), style in zip(selected, styles):
        query = make_query(category, cn, en, style, used_query_keys)
        used_query_keys.add(normalize_query(query))
        result.append((category, query))

    # 与旧版共用历史文件。记录“生成过”的关键词，不保证已搜索成功。
    payload = {
        "used_topics": (old_topics + [x[0] for x in selected])[-500:],
        "used_queries": (
            history["used_queries"] + [query for _, query in result]
        )[-1500:],
    }
    try:
        HISTORY_FILE.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"注意：历史保存失败，跨运行去重将不可用：{exc}")
    return result


def random_wait(min_seconds, max_seconds):
    seconds = random.uniform(min_seconds, max_seconds)
    print(f"等待 {seconds:.1f} 秒")
    time.sleep(seconds)


def save_debug_screenshot(page, round_number):
    filename = f"bing_debug_{round_number}.png"
    try:
        page.screenshot(path=filename, full_page=True, timeout=5000)
        print(f"错误截图：{filename}")
    except PlaywrightError as exc:
        print(f"截图失败：{exc}")


def read_page(page):
    """网页加载后计时 30～60 秒；滚动时间包含在阅读时间内。"""
    read_seconds = random.randint(MIN_BROWSE, MAX_BROWSE)
    scrolls_left = random.randint(MIN_SCROLL, MAX_SCROLL)
    deadline = time.monotonic() + read_seconds
    print(f"开始阅读，计划停留 {read_seconds} 秒（包含滚动时间）")

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        if scrolls_left:
            distance = random.randint(200, 600)
            page.mouse.wheel(0, distance)
            scrolls_left -= 1
            print(f"页面向下滚动 {distance}px")

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        sleep_seconds = min(random.uniform(6, 12), remaining)
        time.sleep(sleep_seconds)
        print(f"阅读剩余时间：{max(0, deadline - time.monotonic()):.1f} 秒")
    print("达到阅读时间，准备返回搜索页面")


def maximize_window(context, page):
    """最大化真实 Edge 窗口；失败不影响搜索。"""
    try:
        session = context.new_cdp_session(page)
        info = session.send("Browser.getWindowForTarget")
        session.send("Browser.setWindowBounds", {
            "windowId": info["windowId"],
            "bounds": {"windowState": "maximized"},
        })
        session.detach()
        print("Edge 窗口已最大化")
    except PlaywrightError as exc:
        print(f"窗口最大化命令未生效，继续运行：{str(exc)[:160]}")


def reset_page_zoom(page):
    """在 Bing 页面将站点缩放恢复为 100%，不进行累积缩放。"""
    try:
        page.keyboard.press("Control+0")
        print("已发送 Ctrl+0，尝试恢复网页 100% 缩放")
    except PlaywrightError as exc:
        print(f"恢复页面缩放失败（不影响搜索）：{str(exc)[:160]}")


def search_bing(page, keyword):
    """直接打开 Bing 搜索结果页，不再触发首页自动补全弹窗。"""
    search_url = f"{BING_URL.rstrip('/')}/search?{urlencode({'q': keyword})}"
    print(f"正在搜索：{keyword}")
    print("直接打开 Bing 搜索结果 URL（不操作首页搜索框）")

    page.goto(search_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    print("实际网址：", page.url)

    # Bing 可在 cn.bing.com 与 www.bing.com 之间重定向，因此只检查路径。
    if not urlsplit(page.url).path.startswith("/search"):
        raise PlaywrightTimeout(
            f"未进入 Bing 搜索结果页，可能存在页面重定向或验证：{page.url}"
        )

    results = page.locator(RESULT_SELECTOR)
    try:
        results.first.wait_for(state="visible", timeout=25000)
    except PlaywrightTimeout:
        print("搜索结果没有显示，请检查截图中的验证码、访问限制或页面结构。")
        raise

    print(f"搜索结果已加载，找到 {results.count()} 条普通结果链接")
    return True


def browse_random_result(page):
    """每轮从 Bing 前三条普通结果随机点击一条，阅读后恢复原页面。"""
    context = page.context
    original_url = page.url
    original_pages = set(context.pages)
    try:
        results = page.locator(RESULT_SELECTOR)
        results.first.wait_for(state="visible", timeout=15000)
        count = min(results.count(), TOP_RESULT_COUNT)
        if not count:
            print("当前没有可点击的普通搜索结果")
            return False

        index = random.randrange(count)
        result = results.nth(index)
        print(f"随机选择第 {index + 1} 条：{result.inner_text(timeout=10000)}")
        print("Bing 结果链接：", result.get_attribute("href"))
        result.scroll_into_view_if_needed(timeout=10000)
        result.click(timeout=15000)

        # Bing 有时在新标签页打开结果，有时在当前页跳转。
        target_page = None
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            new_pages = [tab for tab in context.pages if tab not in original_pages]
            if new_pages:
                target_page = new_pages[-1]
                break
            if page.url != original_url:
                target_page = page
                break
            time.sleep(0.4)
        if target_page is None:
            print("点击后没有检测到页面跳转")
            return False

        try:
            target_page.wait_for_url(
                lambda url: str(url) != "about:blank",
                timeout=15000,
            )
            target_page.wait_for_load_state("load", timeout=LOAD_TIMEOUT)
            print("目标网页常规资源加载完成")
        except PlaywrightTimeout:
            print("部分网页资源未加载完，继续确认正文是否可见")

        # 只要正文正常显示，就开始完整的 30～60 秒阅读计时。
        target_page.locator("body").wait_for(state="visible", timeout=15000)
        if target_page.url == "about:blank":
            print("目标网页尚未打开")
            return False

        print("已进入目标网页：", target_page.url)
        read_page(target_page)
        print("目标网页阅读完成")
        return True
    except (PlaywrightTimeout, PlaywrightError) as exc:
        print(f"点击或浏览网页失败：{str(exc)[:250]}")
        return False
    finally:
        try:
            # 仅关闭本轮新开的页，不关掉 Bing 和用户原有的标签页。
            for tab in list(context.pages):
                if tab not in original_pages:
                    tab.close()
            if not page.is_closed() and page.url != original_url:
                page.goto(original_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
            print("已返回 Bing")
        except PlaywrightError as exc:
            print(f"返回 Bing 失败：{str(exc)[:200]}")


def perform_search(page, keyword):
    search_bing(page, keyword)
    random_wait(2, 5)
    browsed = browse_random_result(page) if CLICK_RESULT else False
    if CLICK_RESULT and not browsed:
        print("本轮未成功进入目标网页")
    return browsed


def main():
    keywords = generate_keywords(SEARCH_COUNT)
    search_success = browse_success = search_failed = 0
    print(f"Bing 搜索：{SEARCH_COUNT} 轮，5 种句式，中英文混合，每轮不同领域")
    print(f"当前首页：{BING_URL}")
    print(f"历史去重文件：{HISTORY_FILE}")
    print(f"浏览器资料目录：{PROFILE_DIR}")
    print(f"网页阅读：每篇 {MIN_BROWSE}～{MAX_BROWSE} 秒")
    print("提醒：独立浏览器资料目录不会自动继承日常 Edge 的登录状态。")

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        # 持久化上下文：保留手动登录的 Cookie；不用 msedgedriver.exe。
        # no_viewport=True：网页视口随实际 Edge 窗口，不再强制 1920×1080。
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="msedge",
            headless=HEADLESS,
            no_viewport=True,
            # 开启 Chromium 沙箱，避免 Edge 提示 --no-sandbox 安全警告。
            chromium_sandbox=True,
            args=["--start-maximized"] if not HEADLESS else [],
        )
        page = context.pages[0] if context.pages else context.new_page()
        if not HEADLESS:
            maximize_window(context, page)

        try:
            # 先进入 Bing 域名，恢复该站点过去可能保存的缩放设置。
            # 只执行一次，不要在每轮使用 Ctrl+-，否则页面会越来越小。
            if not HEADLESS:
                page.goto(BING_URL, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
                reset_page_zoom(page)
                viewport = page.evaluate("""() => ({
                    width: window.innerWidth,
                    height: window.innerHeight,
                    scale: window.devicePixelRatio
                })""")
                print(f"当前网页视口：{viewport['width']}×{viewport['height']}，"
                      f"设备像素比：{viewport['scale']}")

            if PAUSE_FOR_LOGIN:
                print("请在打开的 Edge 中手动登录 Bing / Microsoft 账户。")
                page.goto(BING_URL, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
                input("确认登录完成后，返回终端按 Enter 开始搜索...")

            for i, (category, keyword) in enumerate(keywords, 1):
                print("\n" + "=" * 55)
                print(f"[{i}/{SEARCH_COUNT}] [{category}] 搜索：{keyword}")
                try:
                    browsed = perform_search(page, keyword)
                    search_success += 1
                    if browsed:
                        browse_success += 1
                except (PlaywrightTimeout, PlaywrightError) as exc:
                    search_failed += 1
                    print(f"搜索异常：{str(exc)[:300]}")
                    save_debug_screenshot(page, i)
                    print("遇到页面异常或可能的人机验证，停止后续轮次供人工检查。")
                    break

                if i < SEARCH_COUNT:
                    random_wait(MIN_WAIT, MAX_WAIT)
        except KeyboardInterrupt:
            print("\n用户中止程序")
        finally:
            context.close()
            print(
                f"运行结束：计划 {SEARCH_COUNT}，搜索成功 {search_success}，"
                f"进入网页 {browse_success}，搜索失败 {search_failed}"
            )


if __name__ == "__main__":
    main()
