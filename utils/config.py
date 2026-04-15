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
        raise
        
    return config

def get_llm_config(config, module_name):
    """
    根據模組(如 'summarizer')的 'provider' 設定，從 'llm_providers' 獲取對應的 LLM 配置。
    """
    module_cfg = config.get(module_name, {})
    provider_name = module_cfg.get('provider')
    
    if not provider_name:
        # 向後相容舊格式 (直接在模組下定義 model 等)
        return module_cfg

    provider_cfg = config.get('llm_providers', {}).get(provider_name, {})
    if not provider_cfg:
        print(f"Warning: LLM Provider '{provider_name}' not found in 'llm_providers'. Falling back to module config.")
        return module_cfg

    # 合併 Provider 設定與模組專屬參數 (模組參數優先)
    final_cfg = provider_cfg.copy()
    for key in ['max_tokens', 'temperature']:
        if key in module_cfg:
            final_cfg[key] = module_cfg[key]
    
    return final_cfg

def get_env(key, default=None):
    """獲取環境變數"""
    return os.getenv(key, default)
