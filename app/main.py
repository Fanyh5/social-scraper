from fastapi import FastAPI
from app.api.api import api_router
from app.core.logger import setup_logger

logger = setup_logger("app")

def create_app() -> FastAPI:
    app = FastAPI(
        title="SocialScraper API",
        description="API for scraping social media data",
        version="1.0.0"
    )

    app.include_router(api_router)

    @app.get("/")
    def read_root():
        return {"message": "Welcome to SocialScraper API. Visit /docs for documentation."}
    
    return app

app = create_app()
