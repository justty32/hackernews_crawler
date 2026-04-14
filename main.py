import sys
import argparse
from crawler import run_crawler
from summarizer import run_summarizer
from monitor import run_monitor

def main():
    parser = argparse.ArgumentParser(description="Hacker News 智慧彙報器")
    parser.add_argument("mode", choices=["crawl", "summarize", "monitor", "organize", "all"], 
                        help="""執行模式: 
                        crawl (單次抓取), 
                        summarize (單次總結), 
                        monitor (啟動持續監控), 
                        organize (整理與壓縮舊資料),
                        all (依序執行 crawl 與 summarize)""")
    
    args = parser.parse_args()
    
    if args.mode == "crawl":
        run_crawler()
    elif args.mode == "summarize":
        run_summarizer()
    elif args.mode == "monitor":
        run_monitor()
    elif args.mode == "organize":
        from organizer import run_organizer
        run_organizer()
    elif args.mode == "all":
        print("Starting sequential execution: crawl -> summarize")
        run_crawler()
        run_summarizer()
        print("Done. To start monitoring, use 'python main.py monitor'.")

if __name__ == "__main__":
    main()
