# Hacker News 留言智慧彙報器 (HN Intelligence Reporter)

這是一個結合 Python 抓取、LLM 總結、持續監控與 AI 興趣過濾的整合工具，專為高效吸收 Hacker News 技術動向而設計。

## 🌟 核心特色

- **智慧抓取：** 支援多種過濾條件（關鍵字、熱門排名、留言數門檻）。
- **LLM 總結：** 自動提取冗長留言中的核心觀點。
- **自動化監控：** 背景監控資料夾，並在偵測到新文章總結時，自動進行後續評估。
- **AI 興趣過濾：** 由 AI 代勞評估內容是否符合您的「興趣 Profile」，實現精準提醒。
- **Email 通知：** 偵測到感興趣的文章時，自動發送 Email，第一時間掌握重要資訊。

## 🚀 快速開始

### 1. 安裝與設定
```bash
# 安裝依賴
pip install -r requirements.txt

# 配置環境變數
cp .env.example .env
# 請編輯 .env 填入 API Keys 與 SMTP 帳號密碼
```

### 2. 調整營運參數 (`config.yaml`)
- 設定 `raw_dir` 與 `summary_dir`。
- 在 `crawler` 區塊設定抓取關鍵字與過濾條件。
- 在 `monitoring.interest_profile` 中填寫您感興趣的技術描述。
- 設定 `monitoring.email` 的接收者資訊。

### 3. 執行程式
```bash
# 單次抓取並總結
python main.py all

# 啟動持續監控模式 (背景常駐)
python main.py monitor

# 僅執行特定模組
python main.py crawl      # 僅抓取
python main.py summarize  # 僅總結
```

## 📂 專案結構
- `main.py`: 統一入口點。
- `crawler.py`: 負責抓取與存檔原始資料。
- `summarizer.py`: 負責將原始內容交給 LLM 生成摘要。
- `notifier.py`: AI 興趣度評估與郵件通知發送邏輯。
- `monitor.py`: 常駐服務，監控檔案變動。
- `utils/config.py`: 設定檔與環境變數載入工具。

## 🤖 推薦 LLM 支援
本專案使用 [LiteLLM](https://github.com/BerriAI/litellm)，支援 OpenAI, Anthropic, Gemini, Azure 等各大模型供應商。
