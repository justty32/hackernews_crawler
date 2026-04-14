import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from litellm import completion
from utils.config import load_config, get_env

def evaluate_interest(summary, interest_profile, model_cfg):
    """調用 AI Agent 評估對該摘要的興趣度"""
    prompt = f"""
    你是我的個人 AI 資訊過濾助手。
    請根據我的「興趣設定」，評估以下 Hacker News 文章摘要是否是我感興趣的內容。
    
    我的興趣設定:
    {interest_profile}
    
    文章摘要:
    {summary}
    
    評估要求:
    1. 僅回傳 JSON 格式。
    2. 包含 "interested" (布林值) 與 "reason" (繁體中文原因)。
    3. 如果文章內容與我的興趣高度相關，請將 "interested" 設為 true。
    """
    
    content = ""
    try:
        # 移除 response_format 參數，改為手動解析，以提高對不同模型的相容性
        response = completion(
            model=model_cfg['model'],
            messages=[{"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                      {"role": "user", "content": prompt}],
            api_base=model_cfg.get('api_base')
        )
        content = response.choices[0].message.content
        
        # 移除 Markdown Code Blocks (如果 AI 帶了 ```json ...)
        import json
        clean_content = content.strip()
        if clean_content.startswith("```"):
            clean_content = clean_content.strip("`").strip()
            if clean_content.startswith("json"):
                clean_content = clean_content[4:].strip()
            
        return json.loads(clean_content)
    except Exception as e:
        print(f"Error evaluating interest: {e}. Raw content: {content}")
        return {"interested": False, "reason": f"Evaluation error: {str(e)}"}

def send_email(subject, body, email_cfg):
    """發送 Email 通知"""
    smtp_host = get_env("SMTP_HOST")
    smtp_port = int(get_env("SMTP_PORT", 587))
    smtp_user = get_env("SMTP_USERNAME")
    smtp_pass = get_env("SMTP_PASSWORD")
    recipient = email_cfg['recipient']
    
    if not all([smtp_host, smtp_user, smtp_pass]):
        print("SMTP settings are incomplete. Skipping email notification.")
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
    """處理新生成的摘要：評估並通知"""
    config = load_config()
    monitoring_cfg = config['monitoring']
    model_cfg = config['summarizer']
    
    if not monitoring_cfg.get('enabled', True):
        return
        
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            summary_content = f.read()
            
        # 穩定解析標題
        title = "Unknown Summary"
        for line in summary_content.split('\n'):
            if line.startswith("Original Story: "):
                title = line.replace("Original Story: ", "")
                break
    except Exception as e:
        print(f"Error reading summary file {summary_path}: {e}")
        return
    
    print(f"Evaluating interest for: {title}")
    evaluation = evaluate_interest(summary_content, monitoring_cfg['interest_profile'], model_cfg)
    
    if evaluation.get('interested'):
        print(f"Match found! Sending notification for '{title}'")
        subject = f"{monitoring_cfg['email']['subject_prefix']}{title}"
        body = f"AI 評估原因: {evaluation['reason']}\n\n"
        body += "-" * 20 + "\n"
        body += f"內容摘要:\n{summary_content}"
        
        send_email(subject, body, monitoring_cfg['email'])
    else:
        print(f"No match for '{title}'. Reason: {evaluation.get('reason')}")

if __name__ == "__main__":
    # 測試程式碼
    # process_new_summary("data/summary/2026-04/summary_test.txt")
    pass
