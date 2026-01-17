from fastapi import APIRouter
from app.api.endpoints import twitter

api_router = APIRouter()
api_router.include_router(twitter.router, prefix="/twitter", tags=["twitter"])
