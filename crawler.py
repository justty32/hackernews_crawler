import os
import time
from utils.config import load_config
from services.hn import fetch_item, fetch_top_stories, fetch_comments, format_comments_to_text

def process_story(story_id, config, raw_dir, force=False):
    """處理並儲存單篇 Story"""
    story = fetch_item(story_id)
    if not story:
        return False
        
    title = story.get('title', '')
    url = story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
    descendants = story.get('descendants', 0)
    
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
        f.write(f"Title: {title}\nURL: {url}\nScore: {story.get('score', 0)}\nComments Count: {descendants}\n")
        f.write("-" * 20 + "\nTOP COMMENTS:\n" + comments_text)
    return True

def run_crawler(story_ids=None, force=True):
    config = load_config()
    raw_dir = config['paths']['raw_dir']
    os.makedirs(raw_dir, exist_ok=True)
    
    if story_ids:
        print(f"Fetching targeted IDs: {story_ids} (force={force})")
        for sid in story_ids:
            process_story(sid, config, raw_dir, force=force)
            time.sleep(1)
        return

    crawler_cfg = config['crawler']
    top_ids = fetch_top_stories()
    
    processed_count = 0
    for sid in top_ids[:crawler_cfg['top_limit']]:
        story_data = fetch_item(sid)
        if not story_data: continue
        
        # 基礎過濾
        if story_data.get('descendants', 0) < crawler_cfg['comment_threshold']:
            continue
            
        keywords = crawler_cfg.get('keywords', [])
        if keywords and not any(kw.lower() in story_data.get('title', '').lower() for kw in keywords):
            continue
        
        if process_story(sid, config, raw_dir):
            processed_count += 1
            time.sleep(1)
        
    print(f"Crawler finished. Processed {processed_count} new stories.")

if __name__ == "__main__":
    run_crawler()
