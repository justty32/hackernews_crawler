# Hacker News 智慧技術動向追蹤器 - 技術實作詳解 (Technical Documentation)

這份文件旨在深入解析本專案的原始碼結構與邏輯實作，作為代碼審查（Code Review）與未來維護的參考指南。

---

## 1. 系統架構概覽 (Architecture Overview)

本系統採用 **解耦模組化 (Decoupled Modules)** 架構，並嚴格遵循「單一職責原則 (SRP)」。系統分為四大層級：
1. **調度層 (Orchestrators)**: `crawler.py`, `summarizer.py`, `notifier.py`, `organizer.py`, `monitor.py` 負責流程控制與檔案系統的讀寫。
2. **核心層 (Core)**: `core/evaluator.py` 負責 AI 專家審核的業務邏輯。
3. **服務層 (Services)**: `services/hn.py`, `services/llm.py`, `services/notifiers.py` 負責與外部 API（Hacker News、LLM 供應商、SMTP）對接。
4. **工具層 (Utils)**: `utils/config.py`, `utils/text.py` 提供設定檔解析、HTML 清理與內容截斷等共用工具。

---

## 1.5 AI Agent 支援 (Agent Readiness)
本專案專門為 AI Agent 設計了 `for_agent.md`，提供詳細的 CLI、輸出規格與營運工作流說明，便於自動化整合。

---

## 2. 模組詳解 (Module Breakdown)

### 2.1 服務與工具層 (Services & Utils)
- **`utils/config.py`**:
  - 使用 `utf-8-sig` 讀取 `config.yaml`，確保相容 Windows 系統下的 BOM 標頭。
  - **`get_llm_config(...)`**: 支援「多 Provider」邏輯，可根據模組需求動態切換 OpenAI 或本地 LLM。
- **`utils/text.py`**: 集中處理 HTML 標籤清理與文字智慧截斷（防止 Token 超出 LLM 限制）。
- **`services/hn.py`**: 封裝 Hacker News API 的呼叫邏輯。
- **`services/llm.py`**: 提供統一的 `call_llm` 與 `call_llm_json` 介面，具備 Markdown 標籤自動清理與 JSON 解析容錯。
- **`services/notifiers.py`**: 實作 Email 發送與本地檔案儲存邏輯。

### 2.2 調度層與核心層 (Orchestration & Core)
- **`crawler.py` (資料採集)**:
  - 呼叫 `services/hn.py` 採集原始資料 (`data/raw`)。
  - 支援單一或批量 Story ID 的強制抓取（跳過過濾邏輯）。
- **`summarizer.py` (內容摘要)**:
  - 呼叫 `services/llm.py` 將冗長的留言轉化為精煉的情報 (`data/summary`)。
  - 支援 `--id` 參數，若指定則強制重新生成摘要。
  - 跨月份去重: 遞迴搜尋所有月份目錄，確保文章不重複總結。
- **`core/evaluator.py` & `notifier.py` (核心大腦與通知)**:
  - `notifier.py` 擔任任務協調中心，執行基礎的三層過濾（關鍵字與留言數門檻）。
  - `core/evaluator.py` 負責 **AI 專家審核**，支援動態注入 `category_prompts`。
  - 評估通過後，交由 `services/notifiers.py` 發送通知。
- **`monitor.py` (背景服務)**:
  - 基於 `watchdog` 監控 `data/summary` 目錄，偵測到新摘要時即時觸發 `notifier.py` 進行評估。
- **`organizer.py` (資料整理)**:
  - **自動壓縮**: 超過指定天數的檔案轉為 `.zip` 並分類歸檔。
  - **安全性**: 先驗證壓縮檔大小再刪除原檔，防止歸檔失敗導致資料遺失。

---

## 3. 關鍵技術處理與 Bug 防範 (Critical Fixes)

1. **編碼相容性**: 解決 Windows 環境下 UTF-8 與 BOM 導致的讀取錯誤。
2. **AI 回傳處理**: 處理 Markdown 代碼區塊對 JSON 解析的干擾。
3. **架構解耦**: 將複雜的 API 呼叫與業務邏輯分離，確保代碼易於測試與擴充。

---

## 4. 未來擴充建議

- **Database 整合**: 適合萬級資料量的 SQLite 遷移。
- **Web UI**: 視覺化展示過濾後的技術情報。
