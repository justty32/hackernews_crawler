import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.config import load_config
from notifier import process_new_summary

class SummaryHandler(FileSystemEventHandler):
    def __init__(self, delay=1):
        self.delay = delay
        super().__init__()

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".txt") and "summary_" in os.path.basename(event.src_path):
            print(f"New summary detected: {event.src_path}")
            # 延遲一下確保檔案寫入完成
            time.sleep(self.delay)
            process_new_summary(event.src_path)

def run_monitor():
    config = load_config()
    summary_dir = config['paths']['summary_dir']
    monitoring_cfg = config.get('monitoring', {})
    delay = monitoring_cfg.get('delay', 1)
    os.makedirs(summary_dir, exist_ok=True)
    
    event_handler = SummaryHandler(delay=delay)
    observer = Observer()
    observer.schedule(event_handler, summary_dir, recursive=True)
    
    print(f"Starting monitoring on {summary_dir}...")
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    run_monitor()
