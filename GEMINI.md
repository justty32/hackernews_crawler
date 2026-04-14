# GEMINI.md

## 專案概覽 (Project Overview)
本專案 **Hacker News Crawler** 是一個基於 Python 的工具，旨在從 Hacker News 抓取並下載留言，並整合 LLM 進行智慧化處理。
- **抓取功能：** 支援關鍵字、熱門排行、留言數過濾等模式。
- **儲存與整理：** 原始留言與 LLM 總結分別存放於不同資料夾。總結內容會依據月份分類儲存。
- **持續監控模式：** 自動監控總結資料夾變動。
- **AI 代理/通知：** 整合 AI Agent 根據「興趣 Profile」評估內容，並透過郵件 (Email) 發送提醒。

## 專案類型 (Project Type)
Python 程式專案（含自動化監控與通知服務）。

## 建置與執行 (Building and Running)
- **環境準備：**
  1. 安裝依賴：`pip install -r requirements.txt`
  2. 設定環境變數：參考 `.env.example` 建立 `.env`
  3. 調整設定：修改 `config.yaml`
- **執行命令：**
  - `python main.py crawl`: 執行爬蟲。
  - `python main.py summarize`: 生成摘要。
  - `python main.py monitor`: 啟動持續監控服務。
  - `python main.py all`: 依序執行爬蟲與總結。

## 設定與安全性規範 (Configuration & Security)
- **設定檔 (`config.yaml`)：** 包含路徑、抓取規則、模型參數、興趣 Profile 與郵件接收設定。
- **環境變數 (`.env`)：** 包含 LLM API Keys 與 SMTP 寄件憑證。
- **安全性：** `.gitignore` 已配置排除 `data/`、`.env` 與 `config.yaml`（建議正式環境排除）。

## 開發規範 (Development Conventions)
- **模組化設計：** 爬蟲、總結、監控與入口點邏輯分離，降低耦合。
- **強健性：** 所有網路請求需有 Timeout，所有檔案讀取需有異常處理。
- **AI 整合：** 透過 LiteLLM 實現模型無關性 (Model Agnostic)，支援多種後端。
