import os
import zipfile
import shutil
from datetime import datetime, timedelta
from utils.config import load_config

def get_file_age_days(filepath):
    """獲取檔案最後修改時間距今的天數"""
    mtime = os.path.getmtime(filepath)
    last_modified = datetime.fromtimestamp(mtime)
    return (datetime.now() - last_modified).days

def categorize_content(title, categories_cfg):
    """根據標題判斷所屬分類"""
    for category, keywords in categories_cfg.items():
        if any(kw.lower() in title.lower() for kw in keywords):
            return category
    return "Others"

def archive_files(source_dir, days_threshold, archive_root, categories_cfg, prefix=""):
    """壓縮並封存指定目錄下的舊檔案"""
    if not os.path.exists(source_dir):
        return
    
    os.makedirs(archive_root, exist_ok=True)
    
    # 遍歷所有檔案 (遞迴)
    files_to_archive = []
    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            if not filename.endswith(".txt"):
                continue
            filepath = os.path.join(root, filename)
            if get_file_age_days(filepath) >= days_threshold:
                files_to_archive.append(filepath)
    
    if not files_to_archive:
        print(f"No files in {source_dir} older than {days_threshold} days.")
        return

    print(f"Found {len(files_to_archive)} files to archive from {source_dir}.")
    
    for filepath in files_to_archive:
        filename = os.path.basename(filepath)
        
        # 嘗試讀取標題以進行分類
        title = filename
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.startswith("Title: ") or line.startswith("Original Story: "):
                        title = line.split(": ", 1)[1]
                        break
        except:
            pass
            
        category = categorize_content(title, categories_cfg)
        category_dir = os.path.join(archive_root, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # 建立壓縮檔名 (按月份或分類)
        # 這裡簡單處理：每個檔案轉為一個 zip 或合併？
        # advice.md 建議是 "拿去弄成 .zip"，這裡採集一個月/分類一個 zip 的做法太複雜，
        # 先實現單個檔案壓縮後移動，或按類別打包。
        # 改為：將檔案壓縮到類別目錄下的 zip 中，或者簡單地移動。
        # 考慮到方便查閱，這裡將舊檔案移動到類別目錄，並定期手動或自動打包該目錄。
        # 依照指令 "弄成 .zip"，我們將每個檔案個別壓縮。
        
        zip_filename = f"{os.path.splitext(filename)[0]}.zip"
        zip_path = os.path.join(category_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(filepath, arcname=filename)
            
        os.remove(filepath)
        print(f"Archived: {filename} -> {category}/{zip_filename}")

def run_organizer():
    config = load_config()
    raw_dir = config['paths']['raw_dir']
    summary_dir = config['paths']['summary_dir']
    archive_dir = config['paths']['archive_dir']
    org_cfg = config['organizer']
    
    print("Starting data organization...")
    
    # 整理 raw data
    archive_files(
        source_dir=raw_dir,
        days_threshold=org_cfg['raw_archive_days'],
        archive_root=os.path.join(archive_dir, "raw"),
        categories_cfg=org_cfg['categories']
    )
    
    # 整理 summaries
    archive_files(
        source_dir=summary_dir,
        days_threshold=org_cfg['summary_archive_days'],
        archive_root=os.path.join(archive_dir, "summary"),
        categories_cfg=org_cfg['categories']
    )
    
    print("Organization complete.")

if __name__ == "__main__":
    run_organizer()
