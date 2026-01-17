import yaml
import os
import logging

# 默认配置，作为 fallback
DEFAULT_CONFIG = {
    "log": {
        "level": "INFO",
        "file": None
    },
    "server": {
        "host": "127.0.0.1",
        "port": 8000,
        "reload": False
    },
    "scraper": {
        "twitter": {
            "nitter_instances": [
                "https://nitter.poast.org",
                "https://lightbrd.com"
            ],
            "browser": {
                "headless": True,
                "timeout": 20000,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            }
        }
    }
}

class Config:
    _instance = None
    _config_data = DEFAULT_CONFIG

    @classmethod
    def load(cls, config_path="config.yml"):
        """加载配置文件"""
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        # 简单的深度合并（这里仅做顶层合并，生产环境建议使用专门的合并库）
                        # 这里我们假设 config.yml 结构是完整的，或者我们只覆盖顶层 key
                        # 为了稳健，我们手动合并几个关键 section
                        cls._merge_config(cls._config_data, file_config)
            except Exception as e:
                print(f"Error loading config file {config_path}: {e}")
        else:
            print(f"Config file {config_path} not found, using defaults.")

    @classmethod
    def _merge_config(cls, default, override):
        """递归合并字典"""
        for key, value in override.items():
            if isinstance(value, dict) and key in default and isinstance(default[key], dict):
                cls._merge_config(default[key], value)
            else:
                default[key] = value

    @classmethod
    def get(cls, path=None, default=None):
        """
        获取配置项
        path: 点分隔的路径，例如 "server.port"
        """
        if path is None:
            return cls._config_data
        
        keys = path.split('.')
        value = cls._config_data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

# 初始化加载
Config.load()

def get_config(path=None, default=None):
    return Config.get(path, default)
