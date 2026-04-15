# GEMINI.md

## 專案概覽 (Project Overview)
本專案 **Hacker News Crawler** 是一個基於 Python 的智慧化技術動向追蹤工具。
- **抓取與總結：** 自動抓取熱門文章與留言，並利用 LLM 生成繁體中文摘要。
- **智慧過濾：** 結合「多重關鍵字比對（標題/總結/留言）」、「留言數門檻」與「AI 專家檢查（自定義 Prompt）」的三層過濾機制。
- **自動化監控：** 背景監控總結變動，即時觸發評估。
- **多管道通知：** 支援 Email 與 檔案儲存 (File Storage) 通知，並預留 Telegram/Line 擴充空間。

## 專案類型 (Project Type)
Python 程式專案（含 AI Agent 評估與多管道通知服務）。

## 建置與執行 (Building and Running)
- **執行命令：**
  - `python main.py crawl`: 抓取原始資料。
  - `python main.py summarize`: 生成摘要。
  - `python main.py monitor`: 啟動背景監控與 AI 興趣評估服務。
  - `python main.py organize`: 整理並壓縮舊資料（按天數與分類）。
  - `python main.py all`: 執行抓取+總結。

## 設定與安全性規範 (Configuration & Security)
- **`config.yaml`**:
  - `crawler`: 設定抓取範圍與基礎過濾。
  - `summarizer.dynamic_prompts`: 設定特定領域的總結指令。
  - `monitoring.rules`: 設定基礎過濾規則。
  - `monitoring.category_prompts`: 設定特定領域的 AI 專家評估指令。
  - `organizer`: 設定資料封存天數與分類關鍵字。
- **`.env`**: 存放 API Keys 與 SMTP 憑證。

## 開發規範 (Development Conventions)
- **通知內容：** 必須包含文章標題、HN 連結、留言數、AI 評估原因及總結內容。
- **擴充性：** 通知邏輯集中於 `notifier.py`，便於未來整合其他 Webhook 或 API。
- **穩定性：** AI 評估採手動 JSON 解析，並具備 Markdown 標籤自動清理功能。

---
## ✅ 實作進度更新 (2026-04-15)
- [x] **批量處理 (Batch Processing)**：
    - 支援透過 `--id` (多個 ID) 與 `--url` (多個網址) 指定文章。
    - 支援透過 `--idf` 與 `--urlf` 從檔案批次讀取目標。
    - 手動指定時自動跳過過濾條件，並支援強制重新生成摘要。
- [x] **多後端 LLM 整合**：
    - 實作 `llm_providers` 結構，支援 OpenAI、Ollama 與 LM Studio 並行。
    - 支援針對不同任務 (摘要 vs 評估) 分配不同的 LLM 後端。
- [x] **資料壓縮與歸檔**：已實作 `organizer.py`，支援分類壓縮與過期刪除安全邏輯。
- [x] **系統穩定性**：統一處理 Windows BOM 編碼、Token 智慧截斷與 JSON 解析容錯。
