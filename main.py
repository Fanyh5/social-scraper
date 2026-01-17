import argparse
import uvicorn
from app.core.logger import setup_logger
from app.core.config import get_config

logger = setup_logger("main")

def main():
    parser = argparse.ArgumentParser(description="SocialScraper API Server")
    
    # 从配置中获取默认值
    default_host = get_config("server.host", "127.0.0.1")
    default_port = get_config("server.port", 8000)
    default_reload = get_config("server.reload", False)

    parser.add_argument("--host", default=default_host, help=f"监听主机 (默认: {default_host})")
    parser.add_argument("--port", type=int, default=default_port, help=f"监听端口 (默认: {default_port})")
    
    if default_reload:
        parser.add_argument("--no-reload", action="store_false", dest="reload", help="禁用热重载")
        parser.set_defaults(reload=True)
    else:
        parser.add_argument("--reload", action="store_true", help="启用热重载 (开发模式)")

    # 解析参数
    args = parser.parse_args()
    
    logger.info(f"启动 API 服务在 http://{args.host}:{args.port}")
    # 注意这里引用的 app 路径变了
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()
