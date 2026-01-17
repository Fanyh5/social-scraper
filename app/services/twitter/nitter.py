import sys
import json
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from app.core.logger import setup_logger
from app.core.config import get_config
from app.core.user_agent import get_random_user_agent

logger = setup_logger(__name__)

def scrape_nitter(username, limit=10):
    """
    使用 Playwright 抓取 Nitter 实例的推文
    
    参数:
        username: Twitter 用户名
        limit: 限制抓取的推文数量
    """
    # 从配置获取实例列表
    nitter_instances = get_config("scraper.twitter.nitter_instances", [])
    if not nitter_instances:
        logger.error("未配置 Nitter 实例列表 (scraper.twitter.nitter_instances)")
        return {"author": {}, "tweet": []}

    # 从配置获取浏览器选项
    browser_config = get_config("scraper.twitter.browser", {})
    headless = browser_config.get("headless", True)
    timeout = browser_config.get("timeout", 20000)
    
    # 获取随机 User-Agent
    user_agent = get_random_user_agent()
    logger.info(f"Using User-Agent: {user_agent}")

    results = []
    author_info = {}
    
    with sync_playwright() as p:
        # 启动浏览器
        # 增加 args 模拟真实浏览器特征，绕过部分简单检测
        browser = p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # 创建上下文，设置 User-Agent 和视口大小
        context = browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York"
        )
        
        # 应用 stealth 模式以隐藏自动化特征
        stealth = Stealth()
        stealth.apply_stealth_sync(context)
        
        page = context.new_page()

        # 遍历尝试所有实例
        for instance in nitter_instances:
            url = f"{instance}/{username}"
            logger.info(f"正在尝试实例: {instance} ...")
            
            try:
                # 访问页面
                response = page.goto(url, timeout=timeout, wait_until="domcontentloaded")
                
                # 检查 HTTP 状态码
                # 注意：Nitter 的反爬盾 (Cloudflare/DDOS-Guard) 通常会先返回 503 或 403
                # 浏览器会自动执行 JS 并刷新，所以这里不能直接因为 503 就退出
                if response:
                    if response.status == 404:
                        logger.error(f"实例 {instance} 返回 404: 用户不存在")
                        # 404 说明用户确实不存在，换其他实例也一样，可以直接结束
                        # 但为了稳妥，这里我们还是继续下一个实例，除非我们确定该实例是完全可靠的
                        # 原始逻辑是 continue，这里保持一致
                        continue
                    elif response.status >= 400:
                        logger.warning(f"实例 {instance} 返回状态码 {response.status} (可能是反爬盾)，继续尝试等待页面加载...")

                # 尝试绕过 Cloudflare / 验证码
                try:
                    # 检查是否进入了 Cloudflare 验证页面
                    # 常见的标题有 "Just a moment..." 或页面包含 "Verify you are human"
                    page_title = page.title()
                    page_content = page.content()
                    
                    if "Just a moment" in page_title or "Verify you are human" in page_content or "lightbrd.com" in page_title:
                        logger.warning(f"检测到 Cloudflare 验证页面 ({instance})，尝试自动处理...")
                        page.wait_for_timeout(3000)
                        
                        # 遍历所有 frame 寻找 checkbox
                        for frame in page.frames:
                            try:
                                # Cloudflare 的 iframe 通常包含 challenge
                                if "cloudflare" in frame.url or "challenge" in frame.url:
                                    # 查找 checkbox
                                    checkbox = frame.query_selector("input[type='checkbox']")
                                    if checkbox:
                                        logger.info("找到 Cloudflare 验证框，尝试点击...")
                                        checkbox.click()
                                        page.wait_for_timeout(5000) # 等待验证通过跳转
                                    else:
                                        # 有时是 div 形式的点击区域
                                        box = frame.query_selector(".ctp-checkbox-label")
                                        if box:
                                            logger.info("找到 Cloudflare 验证点击区域，尝试点击...")
                                            box.click()
                                            page.wait_for_timeout(5000)
                            except:
                                pass
                except Exception as cf_e:
                    logger.debug(f"Cloudflare 处理异常: {cf_e}")

                # 等待时间线加载或错误提示
                try:
                    # 优先等待推文列表元素 (.timeline-item)
                    # 给予足够的时间让 JS 盾 (Cloudflare/DDOS-Guard) 完成验证
                    page.wait_for_selector(".timeline-item", timeout=15000)

                    # --- 提取用户信息 ---
                    try:
                        # 尝试查找 profile-card (Nitter 标准结构)
                        profile_card = page.query_selector(".profile-card")
                        
                        # 如果没找到，尝试记录 HTML 片段以便调试
                        if not profile_card:
                            logger.warning(f"未找到 .profile-card 元素. 页面标题: {page.title()}")
                        
                        # 定义提取函数，支持从 profile_card 或 page 提取
                        def get_text(selector, container=page):
                            elem = container.query_selector(selector)
                            return elem.inner_text().strip() if elem else None

                        def get_attr(selector, attr, container=page):
                            elem = container.query_selector(selector)
                            return elem.get_attribute(attr) if elem else None

                        # 1. 头像
                        avatar_href = get_attr(".profile-card-avatar", "href")
                        if avatar_href:
                            if avatar_href.startswith("/"):
                                avatar_href = f"{instance}{avatar_href}"
                            author_info["avatar"] = avatar_href
                        
                        # 2. 名字
                        author_info["name"] = get_text(".profile-card-fullname")
                            
                        # 3. 用户名
                        author_info["username"] = get_text(".profile-card-username")
                            
                        # 4. 简介
                        author_info["bio"] = get_text(".profile-bio")
                            
                        # 5. 位置
                        author_info["location"] = get_text(".profile-location")
                            
                        # 6. 网站
                        author_info["website"] = get_text(".profile-website")
                            
                        # 7. 加入时间
                        author_info["joined"] = get_attr(".profile-joindate", "title") or get_text(".profile-joindate")
                            
                        # 8. 统计数据
                        stats = {}
                        stats["posts"] = get_text(".posts .profile-stat-num")
                        stats["following"] = get_text(".following .profile-stat-num")
                        stats["followers"] = get_text(".followers .profile-stat-num")
                        stats["likes"] = get_text(".likes .profile-stat-num")
                        
                        # 清理 stats 中的 None
                        stats = {k: v.replace(",", "") if v else "0" for k, v in stats.items()}
                        author_info["stats"] = stats
                        
                        # 9. Banner
                        banner_src = get_attr(".profile-banner img", "src")
                        if banner_src:
                            if banner_src.startswith("/"):
                                banner_src = f"{instance}{banner_src}"
                            author_info["banner"] = banner_src

                        logger.info(f"提取用户信息完成: {author_info.get('name', 'Unknown')}")
                        
                    except Exception as e:
                        logger.warning(f"提取用户信息出现异常: {e}")
                        pass
                    
                    # 提取所有推文元素
                    tweets_elements = page.query_selector_all(".timeline-item")
                    
                    if not tweets_elements:
                        logger.warning(f"实例 {instance} 页面加载成功但未找到推文元素")
                        continue
                        
                    logger.info(f"✅ 成功从 {instance} 获取到页面，开始解析...")
                    
                    for i, tweet in enumerate(tweets_elements):
                        if i >= limit:
                            break
                            
                        # 提取数据结构
                        tweet_data = {}
                        
                        # 1. 内容
                        content_elem = tweet.query_selector(".tweet-content")
                        tweet_data["content"] = content_elem.inner_text() if content_elem else ""
                        
                        # 2. 发布时间
                        date_elem = tweet.query_selector(".tweet-date a")
                        tweet_data["published_at"] = date_elem.get_attribute("title") if date_elem else ""
                        
                        # 3. 链接和 ID
                        if date_elem:
                            href = date_elem.get_attribute("href")
                            tweet_data["url"] = f"{instance}{href}"
                            # 从 href 解析 ID: /user/status/123456#m
                            parts = href.split("/status/")
                            if len(parts) > 1:
                                tweet_data["id"] = parts[1].split("#")[0].split("?")[0]
                        
                        # 4. 作者名称
                        author_elem = tweet.query_selector(".fullname")
                        tweet_data["author"] = author_elem.inner_text() if author_elem else ""
                        
                        # 5. 媒体资源 (图片/视频封面)
                        media = []
                        
                        # 5.1 提取普通图片
                        imgs = tweet.query_selector_all(".attachment.image img")
                        for img in imgs:
                            src = img.get_attribute("src")
                            if src:
                                if src.startswith("/"):
                                    src = f"{instance}{src}"
                                media.append(src)
                        
                        # 5.2 提取视频/GIF 封面 (poster 属性)
                        videos = tweet.query_selector_all(".attachment.video-container video")
                        for video in videos:
                            poster = video.get_attribute("poster")
                            if poster:
                                if poster.startswith("/"):
                                    poster = f"{instance}{poster}"
                                media.append(poster)

                        tweet_data["media_urls"] = media
                        
                        results.append(tweet_data)
                    
                    if len(results) > 0:
                        logger.info(f"已成功提取 {len(results)} 条推文")
                        # 成功获取数据后退出循环
                        break
                    
                except Exception as e:
                    # 检查是否是被拦截了
                    content = page.content()
                    if "Verifying your browser" in content:
                        logger.warning(f"实例 {instance} 卡在浏览器验证界面")
                    elif "Rate limit exceeded" in content:
                        logger.warning(f"实例 {instance} 提示速率限制")
                    else:
                        logger.warning(f"实例 {instance} 加载时间线失败: {e}")
                    pass
                        
            except Exception as e:
                logger.error(f"实例 {instance} 连接或导航出错: {e}")
                pass
            
            # 失败后稍作等待再试下一个，避免请求过于密集
            time.sleep(1)
            
        browser.close()
        
    return {
        "author": author_info,
        "tweet": results
    }
