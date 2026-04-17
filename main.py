import sys
import argparse
import os
from urllib.parse import urlparse, parse_qs
from crawler import run_crawler
from summarizer import run_summarizer
from monitor import run_monitor

def extract_id_from_url(url):
    """從 HN 網址提取 story id"""
    try:
        parsed_url = urlparse(url.strip())
        query_params = parse_qs(parsed_url.query)
        if 'id' in query_params:
            return int(query_params['id'][0])
    except Exception as e:
        print(f"Error parsing URL {url}: {e}")
    return None

def read_lines_from_file(file_path):
    """從檔案讀取每一行並清理空白"""
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} not found.")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Hacker News 智慧彙報器")
    parser.add_argument("mode", choices=["crawl", "summarize", "monitor", "organize", "all"], 
                        help="""執行模式: 
                        crawl (單次抓取), 
                        summarize (單次總結), 
                        monitor (啟動持續監控), 
                        organize (整理與壓縮舊資料),
                        all (依序執行 crawl 與 summarize)""")
    
    parser.add_argument("--id", type=int, nargs='+', help="指定要抓取的 Hacker News Story ID (可多個)")
    parser.add_argument("--url", type=str, nargs='+', help="指定要抓取的 Hacker News 網址 (可多個)")
    parser.add_argument("--idf", "--ids_from_file", type=str, nargs='+', help="從檔案讀取 Story IDs (每行一個)")
    parser.add_argument("--urlf", "--urls_from_file", type=str, nargs='+', help="從檔案讀取 HN 網址 (每行一個)")
    parser.add_argument("--dir", type=str, help="指定原始資料目錄 (僅用於 summarize 模式)")
    parser.add_argument("--force", action="store_true", help="強制重新總結 (僅用於 summarize 模式)")
    parser.add_argument("--skip-existing", action="store_true", help="抓取時跳過已存在的檔案 (僅用於手動指定 ID 時)")
    
    args = parser.parse_args()
    
    # 合併所有來源的 ID
    target_ids = []
    
    # 1. 直接指定的 ID
    if args.id:
        target_ids.extend(args.id)
    
    # 2. 直接指定的 URL
    if args.url:
        for url in args.url:
            sid = extract_id_from_url(url)
            if sid: target_ids.append(sid)
            
    # 3. 從檔案讀取的 ID
    if args.idf:
        for fpath in args.idf:
            lines = read_lines_from_file(fpath)
            for line in lines:
                try:
                    target_ids.append(int(line))
                except ValueError:
                    print(f"Skipping invalid ID in file: {line}")

    # 4. 從檔案讀取的 URL
    if args.urlf:
        for fpath in args.urlf:
            lines = read_lines_from_file(fpath)
            for line in lines:
                sid = extract_id_from_url(line)
                if sid: target_ids.append(sid)
    
    # 去重並保持順序
    target_ids = list(dict.fromkeys(target_ids)) if target_ids else None
    
    if args.mode == "crawl":
        run_crawler(story_ids=target_ids, force=not args.skip_existing)
    elif args.mode == "summarize":
        run_summarizer(story_ids=target_ids, custom_raw_dir=args.dir, force=args.force)
    elif args.mode == "monitor":
        run_monitor()
    elif args.mode == "organize":
        from organizer import run_organizer
        run_organizer()
    elif args.mode == "all":
        print(f"Starting sequential execution: crawl -> summarize {'(Target IDs: ' + str(target_ids) + ')' if target_ids else ''}")
        run_crawler(story_ids=target_ids, force=not args.skip_existing)
        run_summarizer(story_ids=target_ids, custom_raw_dir=args.dir, force=args.force)
        print("Done. To start monitoring, use 'python main.py monitor'.")

if __name__ == "__main__":
    main()
