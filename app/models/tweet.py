from pydantic import BaseModel
from typing import List, Optional, Dict

class Tweet(BaseModel):
    id: Optional[str] = None
    url: Optional[str] = None
    content: Optional[str] = None
    published_at: Optional[str] = None
    author: Optional[str] = None
    media_urls: List[str] = []

class Author(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    joined: Optional[str] = None
    stats: Optional[Dict[str, str]] = None
    banner: Optional[str] = None

class TwitterResponse(BaseModel):
    author: Author
    tweet: List[Tweet]
    count: int
    platform: str = "twitter"
