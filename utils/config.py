import os
import yaml
from dotenv import load_dotenv

def load_config(config_path="config.yaml"):
    """載入 YAML 設定檔與環境變數"""
    # 載入 .env
    load_dotenv()
    
    # 載入 YAML
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
        
    try:
        with open(config_path, "r", encoding="utf-8-sig") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading config file {config_path}: {e}")
        # 如果失敗，回傳基本結構避免崩潰，或者根據需求拋出錯誤
        raise
        
    return config

def get_env(key, default=None):
    """獲取環境變數"""
    return os.getenv(key, default)
