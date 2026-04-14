import os
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from litellm import completion
from utils.config import load_config, get_env
from datetime import datetime

def evaluate_with_ai(summary_content, raw_content, title, mon_cfg, model_cfg):
    """調用 AI 進行最終興趣與專業度檢查，支持動態 Prompt"""
    base_prompt = mon_cfg['rules']['expert_check_prompt']
    category_prompts = mon_cfg.get('category_prompts', {})
    
    # 根據標題注入分類特定的 Prompt
    extra_prompts = []
    for category, extra_prompt in category_prompts.items():
        if category.lower() in title.lower():
            extra_prompts.append(extra_prompt)
    
    dynamic_instruction = "\n".join(extra_prompts) if extra_prompts else ""
    
    prompt = f"""
    你是我的個人 AI 技術顧問。
    請根據我的「專業檢查要求」，評估以下 Hacker News 文章摘要及其完整留言內容。
    
    專業檢查要求:
    {base_prompt}
    {dynamic_instruction}
    
    文章摘要:
    {summary_content}
    
    部分完整留言:
    {raw_content[:3000]}
    
    評估要求:
    1. 僅回傳 JSON 格式。
    2. 包含 "passed" (布林值，是否通過檢查) 與 "reason" (繁體中文原因)。
    3. 如果符合檢查要求，請將 "passed"設為 true。
    """
    
    content = ""
    try:
        response = completion(
            model=model_cfg['model'],
            messages=[{"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                      {"role": "user", "content": prompt}],
            api_base=model_cfg.get('api_base'),
            max_tokens=model_cfg.get('max_tokens', 500),
            temperature=model_cfg.get('temperature', 0.1) # 評估時通常使用較低的 temperature
        )
        content = response.choices[0].message.content
        
        # 移除 Markdown Code Blocks
        clean_content = content.strip()
        if clean_content.startswith("```"):
            clean_content = clean_content.strip("`").strip()
            if clean_content.startswith("json"):
                clean_content = clean_content[4:].strip()
            
        return json.loads(clean_content)
    except Exception as e:
        print(f"Error evaluating interest with AI: {e}. Content: {content}")
        return {"passed": False, "reason": f"AI Evaluation failed: {str(e)}"}

def save_to_file(subject, body, output_dir):
    """將通知內容存入指定資料夾"""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Subject: {subject}\n")
        f.write("=" * 30 + "\n")
        f.write(body)
    print(f"Notification saved to folder: {filepath}")

def send_email(subject, body, email_cfg):
    """發送 Email 通知"""
    smtp_host = get_env("SMTP_HOST")
    smtp_port = int(get_env("SMTP_PORT", 587))
    smtp_user = get_env("SMTP_USERNAME")
    smtp_pass = get_env("SMTP_PASSWORD")
    recipient = email_cfg['recipient']
    
    if not all([smtp_host, smtp_user, smtp_pass]):
        print("SMTP settings incomplete. Skipping email.")
        return False
        
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = smtp_user
    msg['To'] = recipient
    
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [recipient], msg.as_string())
        server.quit()
        print(f"Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def process_new_summary(summary_path):
    """多階段過濾：關鍵字比對 -> 留言數門檻 -> AI 專家檢查 -> 多管道通知"""
    config = load_config()
    mon_cfg = config['monitoring']
    model_cfg = config['summarizer']
    rules = mon_cfg['rules']
    
    if not mon_cfg.get('enabled', True):
        return

    # 1. 讀取摘要檔案
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            summary_content = f.read()
    except Exception as e:
        print(f"Error reading summary {summary_path}: {e}")
        return

    # 提取基本資訊
    lines = summary_content.split('\n')
    title = next((l.replace("Original Story: ", "") for l in lines if l.startswith("Original Story: ")), "Unknown")
    story_id = next((l.replace("Story ID: ", "") for l in lines if l.startswith("Story ID: ")), "")

    # 2. 讀取原始檔案 (檢查留言關鍵字與連結)
    raw_path = os.path.join(config['paths']['raw_dir'], f"{story_id}.txt")
    raw_content = ""
    hn_url = f"https://news.ycombinator.com/item?id={story_id}"
    comment_count = 0
    if os.path.exists(raw_path):
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            # 簡單提取連結與留言數
            for line in raw_content.split('\n'):
                if line.startswith("URL: "): hn_url = line.replace("URL: ", "")
                if line.startswith("Comments Count: "): comment_count = int(line.replace("Comments Count: ", ""))

    # 3. 基礎過濾 (標題關鍵字, 總結關鍵字, 留言關鍵字, 留言數)
    match_found = False
    reasons = []

    if any(kw.lower() in title.lower() for kw in rules['title_keywords']):
        match_found = True; reasons.append("Title Keywords Match")
    if any(kw.lower() in summary_content.lower() for kw in rules['summary_keywords']):
        match_found = True; reasons.append("Summary Keywords Match")
    if any(kw.lower() in raw_content.lower() for kw in rules['comment_keywords']):
        match_found = True; reasons.append("Comment Keywords Match")
    
    if comment_count < rules['min_comments']:
        print(f"Skipping '{title}': Comments count {comment_count} < {rules['min_comments']}")
        return

    if not match_found and rules['title_keywords']: # 如果有設關鍵字但沒對上
        print(f"Skipping '{title}': No basic keywords matched.")
        return

    # 4. AI 專業檢查
    print(f"Running AI Expert Check for: {title} (Basic matches: {reasons})")
    ai_eval = evaluate_with_ai(summary_content, raw_content, title, mon_cfg, model_cfg)
    
    if not ai_eval.get('passed'):
        print(f"AI Check Rejected for '{title}': {ai_eval.get('reason')}")
        return

    # 5. 多管道通知
    print(f"Interest Match Confirmed! Sending notifications for: {title}")
    
    # 格式化通知內容
    subject = f"{mon_cfg['channels']['email']['subject_prefix']}{title}"
    body = f"🚀 感興趣文章提醒: {title}\n"
    body += f"🔗 HN 連結: {hn_url}\n"
    body += f"💬 留言數量: {comment_count}\n"
    body += f"💡 AI 評估原因: {ai_eval.get('reason')}\n"
    body += "\n" + "-" * 30 + "\n"
    body += f"📄 文章總結:\n{summary_content}\n"
    
    # 執行所有啟用的通知管道
    channels = mon_cfg['channels']
    if channels['email']['enabled']:
        send_email(subject, body, channels['email'])
    if channels['file']['enabled']:
        save_to_file(subject, body, channels['file']['output_dir'])

if __name__ == "__main__":
    pass
