import requests
import os
import json
import time
from datetime import datetime
from utils.config import load_config

# HN API Base URL
API_BASE = "https://hacker-news.firebaseio.com/v0"

def fetch_hn_item(item_id):
    """抓取單個 HN 項目 (文章或留言)"""
    try:
        response = requests.get(f"{API_BASE}/item/{item_id}.json", timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error fetching item {item_id}: {e}")
        return None

def fetch_comments(item, depth=2, max_comments=10):
    """遞迴抓取留言"""
    if depth == 0 or 'kids' not in item:
        return []
    
    comments = []
    for kid_id in item['kids'][:max_comments]:
        comment_item = fetch_hn_item(kid_id)
        if comment_item and not comment_item.get('deleted') and not comment_item.get('dead'):
            text = comment_item.get('text', '')
            # 清理 HTML 標籤 (簡單處理)
            text = text.replace('<p>', '\n').replace('</p>', '').replace('<i>', '').replace('</i>', '')
            comments.append({
                'author': comment_item.get('by'),
                'text': text,
                'replies': fetch_comments(comment_item, depth - 1, max_comments=3)
            })
    return comments

def format_comments_to_text(comments, level=0):
    """將留言清單轉換為易讀的純文字格式"""
    output = ""
    for comment in comments:
        indent = "  " * level
        output += f"{indent}- {comment['author']}: {comment['text']}\n"
        output += format_comments_to_text(comment['replies'], level + 1)
    return output

def process_story(story_id, config, raw_dir, force=False):
    """處理並儲存單篇 Story"""
    story = fetch_hn_item(story_id)
    if not story:
        print(f"Failed to fetch story {story_id}")
        return False
        
    title = story.get('title', '')
    score = story.get('score', 0)
    descendants = story.get('descendants', 0)
    url = story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
    
    # 檢查是否已下載
    filename = f"{story_id}.txt"
    filepath = os.path.join(raw_dir, filename)
    if not force and os.path.exists(filepath):
        print(f"Skipping {story_id} (already exists)")
        return False
        
    print(f"Processing Story: {title} ({descendants} comments)")
    
    # 抓取留言
    comments = fetch_comments(story)
    comments_text = format_comments_to_text(comments)
    
    # 寫入檔案
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Title: {title}\n")
        f.write(f"URL: {url}\n")
        f.write(f"Score: {score}\n")
        f.write(f"Comments Count: {descendants}\n")
        f.write("-" * 20 + "\n")
        f.write("TOP COMMENTS:\n")
        f.write(comments_text)
    return True

def run_crawler(story_ids=None):
    config = load_config()
    raw_dir = config['paths']['raw_dir']
    os.makedirs(raw_dir, exist_ok=True)
    
    if story_ids:
        print(f"Manually fetching {len(story_ids)} stories: {story_ids}...")
        for sid in story_ids:
            if process_story(sid, config, raw_dir, force=True):
                print(f"Successfully processed story {sid}")
            time.sleep(1) # 避免速率限制
        return

    crawler_cfg = config['crawler']
    
    # 取得 Top Stories
    print("Fetching top stories...")
    try:
        response = requests.get(f"{API_BASE}/topstories.json", timeout=10)
        top_ids = response.json()
    except Exception as e:
        print(f"Failed to fetch top stories: {e}")
        return
    
    processed_count = 0
    for sid in top_ids[:crawler_cfg['top_limit']]:
        story_data = fetch_hn_item(sid)
        if not story_data: continue
        
        # 篩選條件 (僅在自動模式下套用)
        descendants = story_data.get('descendants', 0)
        if descendants < crawler_cfg['comment_threshold']:
            continue
            
        keywords = crawler_cfg.get('keywords', [])
        title = story_data.get('title', '')
        if keywords:
            if not any(kw.lower() in title.lower() for kw in keywords):
                continue
        
        if process_story(sid, config, raw_dir):
            processed_count += 1
            time.sleep(1) # 避免 API 限制
        
    print(f"Crawler finished. Processed {processed_count} new stories.")

if __name__ == "__main__":
    run_crawler()
