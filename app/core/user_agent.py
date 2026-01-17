import random
from app.core.config import get_config

def get_random_user_agent() -> str:
    """
    随机获取一个 User-Agent。
    首先尝试从配置文件中读取 user_agents 列表。
    如果配置中没有或列表为空，则使用默认的硬编码列表。
    """
    
    # 默认的 User-Agent 列表 (作为后备)
    default_user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"
    ]

    # 从配置获取
    configured_agents = get_config("scraper.user_agents", [])
    
    # 如果配置了且不为空，则使用配置的列表
    if configured_agents and isinstance(configured_agents, list):
        return random.choice(configured_agents)
    
    # 否则使用默认列表
    return random.choice(default_user_agents)
