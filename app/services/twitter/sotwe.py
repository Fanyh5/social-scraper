from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from app.core.logger import setup_logger
from app.core.config import get_config
from app.core.user_agent import get_random_user_agent
import time

logger = setup_logger(__name__)

def scrape_sotwe(username, limit=10):
    """
    通过 Sotwe.com 抓取推文 (作为 Nitter 的备选)
    """
    url = f"https://www.sotwe.com/{username}"
    logger.info(f"正在通过 Sotwe 抓取用户: {username}")

    # 从配置获取浏览器选项
    browser_config = get_config("scraper.twitter.browser", {})
    headless = browser_config.get("headless", True)
    timeout = browser_config.get("timeout", 20000)
    
    user_agent = get_random_user_agent()
    logger.info(f"Using User-Agent: {user_agent}")

    results = []
    author_info = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        
        stealth = Stealth()
        stealth.apply_stealth_sync(context)
        
        page = context.new_page()
        
        try:
            response = page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            
            if response and response.status == 404:
                logger.error(f"Sotwe 返回 404: 用户不存在")
                return {"author": {}, "tweet": []}

            # 等待内容加载
            page.wait_for_timeout(2000)
            
            # Sotwe 的结构可能变化，这里基于常见结构尝试提取
            # 通常推文在特定的容器中
            
            # 尝试提取作者信息
            try:
                # 这是一个通用的尝试，具体选择器可能需要根据实际页面调整
                # 假设页面标题或 meta 标签包含信息
                title = page.title()
                author_info["name"] = title.split("|")[0].strip() if "|" in title else username
                author_info["username"] = username
                
                # 尝试从 meta description 获取简介
                desc_meta = page.query_selector("meta[name='description']")
                if desc_meta:
                    author_info["description"] = desc_meta.get_attribute("content")
            except Exception as e:
                logger.warning(f"Sotwe 作者信息提取失败: {e}")

            # 提取推文
            # Sotwe 推文列表通常在某个 flex 容器中
            # 查找所有可能的推文容器
            # 这里使用比较宽泛的选择器，然后过滤
            
            # 滚动几次以加载更多
            for _ in range(2):
                page.mouse.wheel(0, 1000)
                page.wait_for_timeout(500)

            tweet_elements = page.query_selector_all("div.flex.flex-col.gap-2 > div") 
            # 如果上面的选择器失效，尝试更通用的
            if not tweet_elements:
                 tweet_elements = page.query_selector_all("div.p-3")

            count = 0
            for el in tweet_elements:
                if count >= limit:
                    break
                    
                try:
                    text_el = el.query_selector("div[dir='auto']") or el.query_selector("p")
                    if not text_el:
                        continue
                        
                    text = text_el.inner_text()
                    
                    # 尝试提取时间
                    date_el = el.query_selector("time") or el.query_selector("a[href*='/status/']")
                    date = date_el.inner_text() if date_el else ""
                    
                    # 尝试提取链接
                    link = ""
                    link_el = el.query_selector("a[href*='/status/']")
                    if link_el:
                        href = link_el.get_attribute("href")
                        if href:
                             link = f"https://twitter.com{href}" if href.startswith("/") else href

                    results.append({
                        "text": text,
                        "created_at": date,
                        "link": link,
                        "is_retweet": False # Sotwe 较难区分，暂定 False
                    })
                    count += 1
                except Exception as e:
                    continue

        except Exception as e:
            logger.error(f"Sotwe 抓取异常: {e}")
        finally:
            browser.close()

    return {
        "author": author_info,
        "tweet": results
    }
