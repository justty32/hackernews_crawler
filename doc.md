# Hacker News 智慧技術動向追蹤器 - 技術實作詳解 (Technical Documentation)

這份文件旨在深入解析本專案的原始碼結構與邏輯實作，作為代碼審查（Code Review）與未來維護的參考指南。

---

## 1. 系統架構概覽 (Architecture Overview)

本系統採用 **解耦模組化 (Decoupled Modules)** 架構，透過「檔案系統」作為各模組間的資料交換中心：
1.  **Crawler**: 採集原始資料 (`data/raw`)。
2.  **Summarizer**: 生成摘要內容 (`data/summary`)。
3.  **Monitor**: 監控變動並觸發過濾 (`notifier.py`)。
4.  **Notifier**: 執行三層過濾與多管道通知。
- **Organizer**: 執行資料生命週期管理（壓縮、歸檔）。

---

## 1.5 AI Agent 支援 (Agent Readiness)
本專案專門為 AI Agent 設計了 `for_agent.md`，提供詳細的 CLI、輸出規格與營運工作流說明，便於自動化整合。

---

## 2. 模組詳解 (Module Breakdown)


### 2.1 基礎配置: `utils/config.py`
負責系統的營運參數與敏感資訊加載。
- **編碼支援**: 使用 `utf-8-sig` 讀取 `config.yaml`，確保相容 Windows 系統下的 BOM 標頭。
- **`get_llm_config(...)`**: 新增支援「多 Provider」邏輯，可根據模組需求動態切換 OpenAI 或本地 LLM。

### 2.2 資料採集: `crawler.py`
與 Hacker News API 對接，進行初步過濾。
- **`process_story(...)`**: 抽取出的核心邏輯，支援單一 Story ID 的強制抓取。
- **篩選邏輯**: 支援標題關鍵字與留言數門檻篩選（手動指定 ID 時會跳過篩選）。

### 2.3 內容摘要: `summarizer.py`
- **單一 ID 處理**: 支援 `--id` 參數，若指定則強制重新生成摘要。
- **內容截斷**: 自動對輸入文本進行 8000 字元的截斷，防止 Token 超出 LLM 限制。
- **跨月份去重**: 遞迴搜尋 `data/summary` 下的所有月份目錄，確保文章不重複總結。
- **動態 Prompt**: 支援 `get_dynamic_prompt` 根據標題自動附加專家指令。

### 2.4 核心大腦: `notifier.py`
實作「三層過濾機制」與多管道通知。
- **AI 專家審核**: 
    - 支援 `category_prompts` 動態注入。
    - 實作手動 JSON 清理邏輯，提升解析成功率。
- **通知管道**: 目前支援 Email 發送與 File 檔案儲存。

### 2.5 背景服務: `monitor.py`
- 基於 `watchdog` 的監控系統。
- 支援可配置的 `delay` 時間（預設 1 秒），確保檔案寫入完整性。

### 2.6 資料整理: `organizer.py`
- **自動壓縮**: 超過指定天數的檔案轉為 `.zip`。
- **安全性**: 先驗證壓縮檔大小再刪除原檔，防止歸檔失敗導致資料遺失。
- **智慧分類**: 按標題關鍵字自動歸檔至子資料夾。

---

## 3. 關鍵技術處理與 Bug 防範 (Critical Fixes)

1.  **編碼相容性**: 解決 Windows 環境下 UTF-8 與 BOM 導致的讀取錯誤。
2.  **AI 回傳處理**: 處理 Markdown 代碼區塊對 JSON 解析的干擾。
3.  **邊際情況處理**: 處理空關鍵字清單、超長內容截斷與路徑不存在等異常。

---

## 4. 未來擴充建議

- **Database 整合**: 適合萬級資料量的 SQLite 遷移。
- **Web UI**: 視覺化展示過濾後的技術情報。
