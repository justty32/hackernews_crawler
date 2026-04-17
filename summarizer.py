import os
import time
from datetime import datetime
from utils.config import load_config, get_llm_config
from utils.text import truncate_text
from services.llm import call_llm

def get_dynamic_prompt(title, dynamic_cfg):
    if not dynamic_cfg: return ""
    extra_prompts = [p for kw, p in dynamic_cfg.items() if kw.lower() in title.lower()]
    return "\n".join(extra_prompts) if extra_prompts else ""

def check_summary_exists(summary_dir, story_id):
    if not os.path.exists(summary_dir): return False
    for root, dirs, files in os.walk(summary_dir):
        if f"summary_{story_id}.txt" in files: return True
    return False

def summarize_text(title, text, model_cfg, dynamic_cfg=None):
    extra_instruction = get_dynamic_prompt(title, dynamic_cfg)
    truncated_text = truncate_text(text, limit=8000)
    
    prompt = f"""
    請針對以下 Hacker News 文章的留言進行繁體中文總結。
    
    文章標題: {title}
    留言內容:
    {truncated_text}
    
    {extra_instruction}
    """
    return call_llm(model_cfg, prompt)

def run_summarizer(story_ids=None, custom_raw_dir=None, force=False):
    config = load_config()
    raw_dir = custom_raw_dir if custom_raw_dir else config['paths']['raw_dir']
    summary_dir = config['paths']['summary_dir']
    model_cfg = get_llm_config(config, 'summarizer')
    os.makedirs(summary_dir, exist_ok=True)
    
    if not os.path.exists(raw_dir):
        print(f"Error: Raw directory '{raw_dir}' does not exist.")
        return

    raw_files = [f"{sid}.txt" for sid in story_ids] if story_ids else \
                [f for f in os.listdir(raw_dir) if f.endswith(".txt")]
    
    processed_count = 0
    for filename in raw_files:
        sid = filename.replace(".md", "")
        # 如果不是強制模式，且已經有總結了，就跳過
        if not force and check_summary_exists(summary_dir, sid): continue
        
        raw_path = os.path.join(raw_dir, filename)
        if not os.path.exists(raw_path):
            if story_ids: print(f"Warning: File {raw_path} not found.")
            continue

        with open(raw_path, "r", encoding="utf-8") as f:
            content = f.read()
            title = next((l.replace("Title: ", "") for l in content.split('\n') if l.startswith("Title: ")), "Unknown")

        print(f"Summarizing story {sid}...")
        summary = summarize_text(title, content, model_cfg, model_cfg.get('dynamic_prompts', {}))
        
        if summary:
            month_str = datetime.now().strftime("%Y-%m")
            target_dir = os.path.join(summary_dir, month_str)
            os.makedirs(target_dir, exist_ok=True)
            with open(os.path.join(target_dir, f"summary_{sid}.md"), "w", encoding="utf-8") as f:
                f.write(summary + f"## MetaInfo\n---\nOriginal Story: {title}\nStory ID: {sid}\nGenerated at: {datetime.now()}\n" + "-"*20 + "\n")
            processed_count += 1
            time.sleep(1)
            
    print(f"Summarizer finished. Processed {processed_count} new summaries.")

if __name__ == "__main__":
    run_summarizer()
