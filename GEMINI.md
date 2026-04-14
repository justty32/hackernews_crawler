# GEMINI.md

## 專案概覽 (Project Overview)
本專案 **Hacker News Crawler** 是一個基於 Python 的工具，旨在從 Hacker News 抓取並下載留言，並整合 LLM 進行智慧化處理。
- **抓取功能：** 支援關鍵字、熱門排行、留言數過濾等模式。
- **儲存與整理：** 原始留言與 LLM 總結分別存放於不同資料夾。總結內容會依據時間與類型進行整合與排序。
- **持續監控模式 (監控模式)：** 自動監控彙總資料夾變動。
- **AI 代理/通知：** 整合 AI Agent 評估文章興趣度，並透過郵件 (Email) 提醒使用者感興趣的內容。

## 專案類型 (Project Type)
Python 程式專案（含自動化監控與通知服務）。

## 建置與執行 (Building and Running)
- **前置需求：** Python 3.x, `litellm` (LLM 調用), `watchdog` (監控), `smtplib` (郵件)。
- **執行模式：**
  - **抓取模式：** 單次或排程執行抓取任務。
  - **監控模式：** 背景執行，監控資料夾變動並觸發 AI 評估與通知。
- **待辦事項 (TODO)：**
  - [ ] 實現資料夾分流存放（原始資料 vs. 總結）。
  - [ ] 開發總結內容的自動分類與排序邏輯。
  - [ ] 實作「持續監控模式」：追蹤資料夾變動。
  - [ ] 整合 AI Agent 判斷模型：根據使用者興趣過濾文章。
  - [ ] 實作 Email 通知系統。

## 設定與安全性規範 (Configuration & Security)
- **原則：** 盡可能將營運設定參數化於設定檔中，敏感資訊則強制隔離。
- **設定檔 (`config.yaml`)：**
  - **路徑設定：** 原始資料、總結資料、彙總資料夾的路徑。
  - **抓取邏輯：** 抓取頻率、熱門排名閾值、留言數閾值、關鍵字清單。
  - **LLM 設定：** 使用的模型名稱、API Base URL、Temperature 等。
  - **監控參數：** 監控開關、輪詢間隔。
  - **通知設定：** 收件人信箱、郵件主旨模板、興趣 Profile (描述感興趣的主題)。
- **環境變數 (`.env`)：**
  - **API Key：** `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LITE_LLM_KEY` 等。
  - **郵件憑證：** `SMTP_USERNAME`, `SMTP_PASSWORD`。

## 開發規範 (Development Conventions)
- **目錄結構：** 分離 `data/raw` (原始資料) 與 `data/summary` (總結內容)。
- **AI 評估邏輯：** 呼叫 LLM API 時需從 `config.yaml` 讀取使用者興趣 Profile。
- **安全性：** 嚴禁在程式碼或 `config.yaml` 中包含任何形式的 API Key。
