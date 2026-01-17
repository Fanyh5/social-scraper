from app.core.config import get_config
from app.core.logger import setup_logger
from app.services.twitter.nitter import scrape_nitter
from app.services.twitter.sotwe import scrape_sotwe

logger = setup_logger(__name__)

def scrape_twitter_profile(username: str, limit: int = 10):
    """
    统一的 Twitter 抓取入口。
    根据配置的 sources 优先级依次尝试抓取。
    """
    
    # 获取配置的源列表，默认为先 nitter 后 sotwe
    sources = get_config("scraper.twitter.sources", ["nitter", "sotwe"])
    
    last_exception = None
    
    for source in sources:
        try:
            logger.info(f"Trying source: {source} for user {username}")
            
            data = None
            if source == "nitter":
                data = scrape_nitter(username, limit)
            elif source == "sotwe":
                data = scrape_sotwe(username, limit)
            else:
                logger.warning(f"Unknown source: {source}")
                continue
                
            # 检查数据有效性
            if data and (data.get("tweet") or data.get("author")):
                logger.info(f"Successfully scraped {len(data.get('tweet', []))} tweets from {source}")
                # 标记数据来源
                data["source"] = source
                return data
            else:
                logger.warning(f"Source {source} returned empty data for {username}")
                
        except Exception as e:
            logger.error(f"Error scraping from {source}: {e}")
            last_exception = e
            
    # 如果所有源都失败
    logger.error(f"All sources failed for user {username}")
    if last_exception:
        raise last_exception
    return {"author": {}, "tweet": [], "error": "All sources failed"}
