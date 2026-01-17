from fastapi import APIRouter, HTTPException, Query
from app.services.twitter.nitter import scrape_nitter
from app.core.logger import setup_logger
from app.models.tweet import TwitterResponse

router = APIRouter()
logger = setup_logger("api.twitter")

@router.get("/{username}", response_model=TwitterResponse, summary="抓取 Twitter 用户推文")
def get_twitter_tweets(
    username: str, 
    limit: int = Query(10, ge=1, le=100, description="抓取推文数量限制 (1-100)")
):
    """
    抓取指定 Twitter 用户的推文数据。
    
    - **username**: Twitter 用户名 (不带 @)
    - **limit**: 返回的推文数量限制
    """
    logger.info(f"API Request: Scrape Twitter user {username}, limit={limit}")
    try:
        # scrape_nitter 返回 {"author": {...}, "tweet": [...]}
        data = scrape_nitter(username, limit)
        
        # 如果返回空数据，或者没有找到推文（视业务逻辑而定，这里假设只要没报错就返回）
        if not data["tweet"] and not data["author"]:
             logger.warning(f"No data found for user {username}")
        
        return {
            "author": data.get("author", {}),
            "tweet": data.get("tweet", []),
            "count": len(data.get("tweet", [])),
            "platform": "twitter"
        }
    except Exception as e:
        logger.error(f"Error scraping twitter user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
