長久下來，data/raw會堆積一堆文章，要想個辦法做壓縮。比如新增一個模式：整理，在這模式下會檢查raw中的文章，是否已經超過一個月，超過的話就拿去弄成.zip。
summarize的壓縮則是用三個月或一年。除此之外也要按照我設立的categories做額外的壓縮流檔，比如AI、軟體等。

在做summarize時，也要提供一些我可以設定的prompt，並且可以按照文章關鍵字進行添加減少。比如當文章關鍵字有AI時，我會添加一些prompt如"你是專業的AI科學家"、"對於符號AI部份多加關注"

在evaluate時，可以先進行分段、分categories、分批，來讓AI進行查看，並且也要讓我可以按照tag或類型設定prompt。這部分要精細一些，麻煩你了。

AI專家審核這部份的prompt也如同上面那樣，可以用更靈活的方式去設定

然後是watchdog事件，那個延遲一秒，應該可以在設定檔中做設定

然後是 `crawl`, `summarize`, `monitor`, `all` 四種模式，麻煩多解釋一下。
是否crawl, summarize都是單次執行完就結束，然後monitor是持續執行，然後all是先執行前面兩個，然後持續執行monitor?

---
## ✅ 實作進度更新 (2026-04-14)
- [x] **資料壓縮**：已實作 `organizer.py`，支援對 `data/raw` (30天) 與 `data/summary` (90天) 進行分類壓縮 (.zip)。
- [x] **動態 Prompt (Summarize)**：支援根據標題關鍵字注入專家 Prompt。
- [x] **評估優化**：AI 專家檢查已支援分類特定 Prompt 注入。
- [x] **監控延遲**：延遲時間已抽離至 `config.yaml`。
- [x] **模式說明**：已更新 CLI 幫助文本。`crawl`/`summarize`/`organize` 為單次任務，`monitor` 為常駐監控，`all` 為 `crawl` + `summarize`。
- [x] **系統穩定性與 Bug 修正** (2026-04-14):
    - 修正 `organizer.py` 的壓縮安全邏輯與標題解析錯誤處理。
    - 提升 `monitor.py` 與 `crawler.py` 的配置讀取健壯性 (處理空列表與缺失節點)。
    - `summarizer.py` 增加跨月份目錄的摘要重複檢查與輸入長度截斷 (8000 字元)。
    - `notifier.py` 同步 AI 呼叫參數，確保與總結邏輯一致。
    - `utils/config.py` 改用 `utf-8-sig` 以支援 Windows 下的編碼問題。
