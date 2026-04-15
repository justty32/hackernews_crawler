import os
from utils.config import load_config, get_llm_config
from services.notifiers import send_email, save_to_file
from core.evaluator import evaluate_story

def process_new_summary(summary_path):
    """處理新生成的摘要：過濾 -> 評估 -> 通知"""
    config = load_config()
    mon_cfg = config['monitoring']
    if not mon_cfg.get('enabled', True): return

    model_cfg = get_llm_config(config, 'monitoring')
    rules = mon_cfg['rules']

    # 1. 讀取摘要內容
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_content = f.read()
    
    lines = summary_content.split('\n')
    title = next((l.replace("Original Story: ", "") for l in lines if l.startswith("Original Story: ")), "Unknown")
    story_id = next((l.replace("Story ID: ", "") for l in lines if l.startswith("Story ID: ")), "")

    # 2. 讀取原始資料以獲取更多資訊
    raw_path = os.path.join(config['paths']['raw_dir'], f"{story_id}.txt")
    raw_content = ""
    hn_url, comment_count = f"https://news.ycombinator.com/item?id={story_id}", 0
    if os.path.exists(raw_path):
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            for line in raw_content.split('\n'):
                if line.startswith("URL: "): hn_url = line.replace("URL: ", "")
                if line.startswith("Comments Count: "): comment_count = int(line.replace("Comments Count: ", ""))

    # 3. 基礎過濾 (門檻與關鍵字)
    if comment_count < rules['min_comments']: return
    
    match_found = any(kw.lower() in title.lower() for kw in rules['title_keywords']) or \
                  any(kw.lower() in summary_content.lower() for kw in rules['summary_keywords']) or \
                  any(kw.lower() in raw_content.lower() for kw in rules['comment_keywords'])
    
    if not match_found and rules['title_keywords']: return

    # 4. AI 專業檢查 (調用 core 模組)
    print(f"Running AI Expert Check for: {title}")
    ai_eval = evaluate_story(summary_content, raw_content, title, mon_cfg, model_cfg)
    
    if not ai_eval.get('passed'):
        print(f"AI Rejected: {ai_eval.get('reason')}")
        return

    # 5. 發送通知 (調用 services 模組)
    print(f"Confirmed Interest! Sending notifications for: {title}")
    subject = f"{mon_cfg['channels']['email']['subject_prefix']}{title}"
    body = f"🚀 感興趣文章: {title}\n🔗 HN 連結: {hn_url}\n💬 留言數量: {comment_count}\n💡 AI 評估: {ai_eval.get('reason')}\n\n" + "-"*30 + f"\n📄 文章總結:\n{summary_content}"
    
    channels = mon_cfg['channels']
    if channels['email']['enabled']:
        send_email(subject, body, channels['email'])
    if channels['file']['enabled']:
        save_to_file(subject, body, channels['file']['output_dir'])

if __name__ == "__main__":
    pass
