# Hacker News 智慧技術動向追蹤器 - 技術實作詳解 (Technical Documentation)

這份文件旨在深入解析本專案的原始碼結構與邏輯實作，作為代碼審查（Code Review）與未來維護的參考指南。

---

## 1. 系統架構概覽 (Architecture Overview)

本系統採用 **解耦模組化 (Decoupled Modules)** 架構，透過「檔案系統」作為各模組間的資料交換中心：
1.  **Crawler**: 採集原始資料 (`data/raw`)。
2.  **Summarizer**: 生成摘要內容 (`data/summary`)。
3.  **Monitor**: 監控變動並觸發過濾 (`notifier.py`)。
4.  **Notifier**: 執行三層過濾與多管道通知。

---

## 2. 模組詳解 (Module Breakdown)

### 2.1 基礎配置: `utils/config.py`
負責系統的營運參數與敏感資訊加載。
- **`load_config(config_path)`**: 使用 `PyYAML` 讀取 `config.yaml`。
- **`load_dotenv()`**: 透過 `python-dotenv` 將 `.env` 中的 API Key 加載至環境變數。
- **設計考量**: 實現「營運參數」與「敏感密鑰」的分離，提高安全性與靈活性。

### 2.2 資料採集: `crawler.py`
與 Hacker News API 對接，進行初步過濾。
- **`fetch_hn_item(item_id)`**:
    - 使用 `requests.get` 獲取 JSON 資料。
    - **關鍵點**: 設置了 `timeout=10` 以防網路掛起。
- **`fetch_comments(item, depth, max_comments)`**:
    - **遞迴抓取**: 透過 `kids` 欄位深入抓取留言。
    - **清理**: 簡單清理 HTML 標籤（如 `<p>`, `<i>`），提升後續 LLM 處理效果。
- **`run_crawler()`**:
    - **第一層過濾**: 在抓取階段即根據 `top_limit`、`comment_threshold` 與 `keywords` (標題關鍵字) 進行初步篩選，節省 API 調用次數。
    - **去重**: 檢查 `data/raw/` 是否已存在該文章 ID，避免重複處理。

### 2.3 內容摘要: `summarizer.py`
將冗長的留言轉化為精煉的情報。
- **`summarize_text(title, text, model_cfg)`**:
    - **LiteLLM 整合**: 調用 `completion` 函數，實作模型無關性。
    - **Prompt 設計**: 要求 AI 使用繁體中文，列出核心觀點與社群氛圍，並嚴格控制字數。
- **`run_summarizer()`**:
    - **結構化儲存**: 自動依據「年-月」建立子資料夾（如 `data/summary/2026-04/`），方便長期歸檔。

### 2.4 核心大腦: `notifier.py`
本專案最複雜的邏輯所在地，實作了「三層過濾機制」。
- **`evaluate_with_ai(...)`**:
    - **Context Management**: 將前 3000 字的原始內容傳給 AI，確保其有足夠脈絡進行專家評估。
    - **JSON Robustness**: 
        - 強制要求 AI 輸出 JSON。
        - 實作了手動清理 Markdown 代碼區塊 (` ```json `) 的邏輯，防止 `json.loads` 解析失敗。
- **`process_new_summary(summary_path)`**:
    - **三層過濾流程**:
        1.  **基礎屬性檢查**: 比對標題、摘要、留言中的關鍵字。若有設定關鍵字但完全沒對上，則跳過。
        2.  **門檻檢查**: 再次確認留言總數是否達標。
        3.  **AI 專家審核**: 呼叫 `evaluate_with_ai`，執行使用者的自定義 Prompt（例如尋找專業人士意見）。
- **多管道通知實作**:
    - **`send_email(...)`**: 使用 `smtplib` 進行 TLS 加密傳輸。
    - **`save_to_file(...)`**: 實作基礎通知管道，將通知內容（含連結、原因、摘要）存為檔案。

### 2.5 背景服務: `monitor.py`
實現自動化流程的關鍵。
- **`SummaryHandler(FileSystemEventHandler)`**:
    - 繼承自 `watchdog`，監聽 `on_created` 事件。
    - **關鍵邏輯**: 偵測到新檔案後延遲 1 秒執行，確保檔案寫入已完全結束。
- **`run_monitor()`**:
    - 常駐背景，持續掃描 `data/summary/` 目錄及其子目錄。

### 2.6 統一入口: `main.py`
- 使用 `argparse` 提供 CLI 介面。
- 支援 `crawl`, `summarize`, `monitor`, `all` 四種模式，方便使用者根據場景切換。

---

## 3. 關鍵技術處理與 Bug 防範 (Critical Fixes)

1.  **網路穩定性**: 所有 `requests` 調用均封裝於 `try-except` 並設有 `timeout`。
2.  **資料解析健壯性**: 
    - 檔案讀取時若發生編碼或不存在問題，會捕獲異常並記錄，不中斷主流程。
    - 標題提取採用迴圈比對 `startswith` 而非固定行號，防止檔案格式微調導致的崩潰。
3.  **AI 回傳處理**:
    - 針對不同模型（如 GPT-4 vs. Claude）可能帶有的 Markdown 標籤進行預處理。
    - 提供詳細的 Error Log，包含 AI 回傳的原始內容，方便除錯。

---

## 4. 未來擴充建議

- **Database 整合**: 當資料量達到萬級時，建議從檔案系統遷移至 SQLite。
- **Web UI**: 可建立一個簡單的看板來展示 `data/notifications` 中的內容。
- **更多的通知管道**: 已在 `config.yaml` 預留 Telegram/Line 欄位，只需在 `notifier.py` 中實作對應的 API 呼叫即可。
