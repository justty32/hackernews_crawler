# Hacker News 智慧技術動向追蹤器

本專案結合 Python 抓取、LLM 總結、持續監控與多階段 AI 過濾，幫助您精確捕捉 Hacker News 上的專業見解。

## 🚀 三層過濾機制 (Triple-Filtering)

1.  **基礎篩選：** 根據「標題關鍵字」與「留言數門檻」進行初步篩選。
2.  **關鍵字比對：** 檢查「AI 總結內容」與「原始留言全文」是否包含指定的興趣關鍵字。
3.  **AI 專家檢查：** 調用 AI Agent，根據您提供的自定義 Prompt（如：*「檢查是否有專業人士的實作經驗分享」*）進行最後審核。

## 📢 通知管道 (Notification Channels)

-   **Email 通知：** 第一時間將文章摘要、連結、留言數與 AI 評估原因寄送至您的信箱。
-   **檔案儲存：** 自動將通知內容存入 `data/notifications/`，方便離線查閱或整合其他自動化工具。
-   **未來擴充：** 預留 Telegram, Line 與 雲端儲存 (Google Drive) 的配置介面。

## 🛠️ 配置說明

### 1. 營運設定 (`config.yaml`)
```yaml
monitoring:
  rules:
    title_keywords: ["AI", "Rust"]   # 標題關鍵字
    min_comments: 50                 # 留言數門檻
    expert_check_prompt: "..."       # AI 專家檢查指令
  channels:
    email: { enabled: true }         # 啟用郵件
    file: { enabled: true }          # 啟用檔案存放
```

### 2. 環境變數 (`.env`)
-   `OPENAI_API_KEY`: LLM API 金鑰。
-   `SMTP_USERNAME` / `SMTP_PASSWORD`: 用於發送通知郵件的帳密。

## 🚀 進階功能 (Advanced Features)

1.  **動態 Prompt 注入：** 根據文章類型自動切換 AI 視角（如：AI 科學家、軟體架構師），提供更精準的總結與評估。
2.  **資料自動封存：** 定期將 `data/raw` 與 `data/summary` 中的舊檔案壓縮為 `.zip` 並按類別（AI/Software/Security）歸檔，保持系統清爽。
3.  **可調監控延遲：** 支援在設定檔中調整監控延遲，適應不同的磁碟寫入速度。

## 🏃 執行方式
```bash
# 啟動監控服務 (會自動觸發過濾與通知)
python main.py monitor

# 指定特定文章進行抓取與總結 (忽略過濾門檻)
python main.py all --id 40001234
python main.py all --url https://news.ycombinator.com/item?id=40001234
python main.py all --idf ids.txt    # 從檔案讀取多個 ID
python main.py all --urlf urls.txt  # 從檔案讀取多個網址

# 單次抓取/總結
python main.py crawl --id 40001234
python main.py summarize --url https://news.ycombinator.com/item?id=40001234

# 整理舊資料 (壓縮並歸檔)
python main.py organize
```

### 3. 多 LLM 後端設定 (`config.yaml`)
本專案支援針對不同功能模組設定不同的 LLM Provider (如 OpenAI, Ollama, LM Studio)。
```yaml
llm_providers:
  openai:
    model: "gpt-3.5-turbo"
  ollama:
    model: "ollama/llama3"
    api_base: "http://localhost:11434"

summarizer:
  provider: "openai"    # 生成摘要使用 OpenAI

monitoring:
  provider: "ollama"    # AI 專家評估使用本地 Ollama
```

## 🤖 AI Agent 整合 (Agent Integration)
若您是 AI Agent 並準備運作此工具，請參閱 [for_agent.md](./for_agent.md) 獲取詳細的規格與操作規範。
