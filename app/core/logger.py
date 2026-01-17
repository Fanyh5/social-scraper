import logging
import sys
from app.core.config import get_config

def setup_logger(name=__name__, level=None):
    """
    配置日志记录器
    输出到 stderr 以避免干扰 stdout 的 JSON 输出
    """
    logger = logging.getLogger(name)
    
    # 优先使用传入的 level，否则从配置读取，最后默认为 INFO
    if level is None:
        level_str = get_config("log.level", "INFO").upper()
        level = getattr(logging, level_str, logging.INFO)
    
    logger.setLevel(level)
    
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # stderr handler
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # file handler (if configured)
        log_file = get_config("log.file")
        if log_file:
            try:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                # 避免因为日志文件问题导致程序崩溃，打印错误到 stderr
                sys.stderr.write(f"Failed to setup log file {log_file}: {e}\n")
        
    return logger
