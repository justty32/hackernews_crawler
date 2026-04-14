import sys
import argparse
from crawler import run_crawler
from summarizer import run_summarizer
from monitor import run_monitor

def main():
    parser = argparse.ArgumentParser(description="Hacker News 智慧彙報器")
    parser.add_argument("mode", choices=["crawl", "summarize", "monitor", "all"], 
                        help="執行模式: crawl (抓取), summarize (總結), monitor (監控), all (依序執行 crawl 與 summarize)")
    
    args = parser.parse_args()
    
    if args.mode == "crawl":
        run_crawler()
    elif args.mode == "summarize":
        run_summarizer()
    elif args.mode == "monitor":
        run_monitor()
    elif args.mode == "all":
        run_crawler()
        run_summarizer()

if __name__ == "__main__":
    main()
