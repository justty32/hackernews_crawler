import os
import json
import time
from datetime import datetime
from litellm import completion
from utils.config import load_config, get_env

def get_dynamic_prompt(title, dynamic_cfg):
    """根據標題關鍵字獲取額外的 prompt 指令"""
    extra_prompts = []
    if not dynamic_cfg:
        return ""
    for keyword, extra_prompt in dynamic_cfg.items():
        if keyword.lower() in title.lower():
            extra_prompts.append(extra_prompt)
    return "\n".join(extra_prompts) if extra_prompts else ""

def check_summary_exists(summary_dir, story_id):
    """檢查各月份目錄下是否已存在該摘要"""
    if not os.path.exists(summary_dir):
        return False
    for root, dirs, files in os.walk(summary_dir):
        if f"summary_{story_id}.txt" in files:
            return True
    return False

def summarize_text(title, text, model_cfg, dynamic_cfg=None):
    """調用 LiteLLM 生成摘要，並確保留言截斷在完整區塊"""
    extra_instruction = get_dynamic_prompt(title, dynamic_cfg)
    
    # 智慧截斷邏輯
    limit = 8000
    if len(text) > limit:
        # 尋找 8000 字元前最後一個留言的起始點 (格式為 "\n- ")
        break_point = text[:limit].rfind("\n- ")
        if break_point != -1:
            # 截斷在該留言之前，並加上提示
            truncated_text = text[:break_point] + "\n\n(Part of comments truncated for length...)"
        else:
            # 如果找不到留言格式，則進行硬截斷
            truncated_text = text[:limit]
    else:
        truncated_text = text
    
    prompt = f"""
    請針對以下 Hacker News 文章的留言內容進行簡短總結。
    
    文章標題: {title}
    
    留言內容:
    {truncated_text}
    
    總結要求:
    1. 繁體中文總結。
    2. 列出 3-5 個核心討論觀點。
    3. 總結社群的整體氛圍 (例如: 贊成、反對、技術性討論等)。
    4. 總結字數控制在 300 字以內。
    {extra_instruction}
    """
    
    try:
        response = completion(
            model=model_cfg['model'],
            messages=[{"role": "user", "content": prompt}],
            api_base=model_cfg.get('api_base'),
            max_tokens=model_cfg.get('max_tokens', 500),
            temperature=model_cfg.get('temperature', 0.3)
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during summarization for '{title}': {e}")
        return None

def run_summarizer():
    config = load_config()
    raw_dir = config['paths']['raw_dir']
    summary_dir = config['paths']['summary_dir']
    model_cfg = config['summarizer']
    
    os.makedirs(summary_dir, exist_ok=True)
    
    # 讀取 raw_dir 下的所有檔案
    if not os.path.exists(raw_dir):
        print("No raw data to summarize.")
        return
        
    raw_files = [f for f in os.listdir(raw_dir) if f.endswith(".txt")]
    
    processed_count = 0
    for filename in raw_files:
        story_id = filename.replace(".txt", "")
        
        # 檢查是否已存在摘要 (搜尋所有月份)
        if check_summary_exists(summary_dir, story_id):
            continue
            
        print(f"Summarizing story {story_id}...")
        
        # 依據月份建立子目錄 (存檔時使用當前月份)
        month_str = datetime.now().strftime("%Y-%m")
        target_month_dir = os.path.join(summary_dir, month_str)
        os.makedirs(target_month_dir, exist_ok=True)
        
        summary_filename = f"summary_{story_id}.txt"
        summary_path = os.path.join(target_month_dir, summary_filename)
        
        # 讀取原始內容
        try:
            with open(os.path.join(raw_dir, filename), "r", encoding="utf-8") as f:
                content = f.read()
                
            # 簡單解析標題
            title = "Unknown Title"
            for line in content.split('\n'):
                if line.startswith("Title: "):
                    title = line.replace("Title: ", "")
                    break
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            continue
        
        # 生成摘要
        dynamic_cfg = model_cfg.get('dynamic_prompts', {})
        summary = summarize_text(title, content, model_cfg, dynamic_cfg)
        
        if summary:
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(f"Original Story: {title}\n")
                f.write(f"Story ID: {story_id}\n")
                f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 20 + "\n")
                f.write(summary)
            processed_count += 1
            time.sleep(1) # 避免速率限制
            
    print(f"Summarizer finished. Processed {processed_count} new summaries.")

if __name__ == "__main__":
    run_summarizer()
