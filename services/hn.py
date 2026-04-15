import requests
import time
from utils.text import clean_html

API_BASE = "https://hacker-news.firebaseio.com/v0"

def fetch_item(item_id):
    """抓取單個 HN 項目 (文章或留言)"""
    try:
        response = requests.get(f"{API_BASE}/item/{item_id}.json", timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error fetching HN item {item_id}: {e}")
        return None

def fetch_top_stories():
    """抓取 Top Stories"""
    try:
        response = requests.get(f"{API_BASE}/topstories.json", timeout=10)
        return response.json()
    except Exception as e:
        print(f"Failed to fetch top stories: {e}")
        return []

def fetch_comments(item, depth=2, max_comments=10):
    """遞迴抓取留言"""
    if depth == 0 or 'kids' not in item:
        return []
    
    comments = []
    for kid_id in item['kids'][:max_comments]:
        comment_item = fetch_item(kid_id)
        if comment_item and not comment_item.get('deleted') and not comment_item.get('dead'):
            text = clean_html(comment_item.get('text', ''))
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
