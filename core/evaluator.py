from services.llm import call_llm_json
from utils.text import truncate_text

def evaluate_story(summary, raw_content, title, mon_cfg, model_cfg):
    """AI 專家評估邏輯"""
    base_prompt = mon_cfg['rules']['expert_check_prompt']
    category_prompts = mon_cfg.get('category_prompts', {})
    
    # 注入分類 Prompt
    extra_prompts = [p for cat, p in category_prompts.items() if cat.lower() in title.lower()]
    dynamic_instruction = "\n".join(extra_prompts)
    
    # 截斷內容
    truncated_raw = truncate_text(raw_content, limit=3000)
    
    prompt = f"""
    你是我的個人 AI 技術顧問。評估以下文章摘要及其留言。
    
    專業檢查要求:
    {base_prompt}
    {dynamic_instruction}
    
    文章摘要:
    {summary}
    
    部分留言:
    {truncated_raw}
    
    評估要求:
    1. 僅回傳 JSON: {{"passed": bool, "reason": string}}
    2. 使用繁體中文說明原因。
    """
    
    result = call_llm_json(model_cfg, prompt)
    if result:
        return result
    return {"passed": False, "reason": "AI Evaluation failed to produce valid JSON."}
