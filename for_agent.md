# AI Agent Operating Guide for Hacker News Crawler

This document provides detailed technical specifications, CLI parameters, and operational workflows for AI Agents to interact with the Hacker News Crawler tool.

---

## 1. Tool Overview
The Hacker News Crawler is a modular system designed for autonomous intelligence gathering. It manages the full lifecycle from raw data acquisition to LLM-driven filtering and notification.

## 2. Command Line Interface (CLI)
All operations are routed through `main.py`.

### 2.1 Core Modes
| Mode | Purpose | Recommended Use |
| :--- | :--- | :--- |
| `crawl` | Fetch raw stories and comments from HN. | Use for initial data acquisition. |
| `summarize` | Generate LLM summaries from raw data. | Use to transform raw text into intelligence. |
| `monitor` | Persistent background service for filtering. | Run as a daemon for real-time alerts. |
| `organize` | Data maintenance and archiving. | Run periodically (e.g., daily) to manage disk space. |
| `all` | Chained execution: `crawl` -> `summarize`. | Ideal for scheduled batch processing. |

### 2.2 Advanced Parameters & Flags
| Parameter | Applicable Modes | Description |
| :--- | :--- | :--- |
| `--id ID [ID...]` | `crawl`, `summarize`, `all` | Target specific story IDs. |
| `--url URL [URL...]` | `crawl`, `summarize`, `all` | Target specific HN URLs. |
| `--idf FILE` | `crawl`, `summarize`, `all` | Bulk targets from a line-delimited file of IDs. |
| `--urlf FILE` | `crawl`, `summarize`, `all` | Bulk targets from a line-delimited file of URLs. |
| `--dir DIR_PATH` | `summarize`, `all` | **(New)** Override the default `data/raw` source directory. |
| `--force` | `summarize`, `all` | **(New)** Force re-summarization even if a summary exists in `data/summary/`. |
| `--skip-existing` | `crawl`, `all` | **(New)** Skip fetching if `{id}.txt` exists in `data/raw`, even when targets are manually specified. |

---

## 3. Detailed Operational Logic for Agents

### 3.1 Fetching Logic (`crawl`)
- **Default (No IDs)**: Scrapes Top Stories, applies `comment_threshold` and `keywords` filters. Skips existing files.
- **Manual (With IDs/URLs)**: Bypasses all filters.
  - **Standard Behavior**: Overwrites existing files in `data/raw/` (Force = True).
  - **With `--skip-existing`**: Checks for file existence first. Recommended for Agents resuming a failed bulk job to save API calls/time.

### 3.2 Summarization Logic (`summarize`)
- **Source Selection**: Defaults to `data/raw/`. Use `--dir` to point to archives or staging folders.
- **De-duplication**: Recursively checks `data/summary/` for `summary_{id}.txt`.
  - **Standard Behavior**: Skips IDs that already have a summary to optimize Token usage.
  - **With `--force`**: Ignores existing summaries and generates new ones. Use this if your `summarizer.dynamic_prompts` in `config.yaml` have changed and you need updated insights.

### 3.3 The Monitoring Loop (`monitor`)
- **Mechanism**: Uses `watchdog` to detect `FileCreatedEvent` in the summary directory.
- **Filtering**: Performs Keyword Matching (Title/Summary/Comments) + AI Expert Evaluation.
- **Configuration**: Ensure `monitoring.delay_seconds` in `config.yaml` is tuned to your filesystem speed.

---

## 4. Operational Workflows for Agents (Step-by-Step)

### Scenario A: Targeted Research on a Specific Topic
1.  Populate a text file `targets.txt` with relevant HN URLs.
2.  Run: `python main.py all --urlf targets.txt --skip-existing`.
3.  Check `data/summary/` for the generated insights.

### Scenario B: Periodic Intelligence Pulse
1.  Configure `config.yaml` with your interest keywords and expert prompt.
2.  Run `python main.py all` via a cron job every 4 hours.
3.  Keep `python main.py monitor` running in a separate process/screen.
4.  Consume JSON/Text outputs from `data/notifications/`.

### Scenario C: Re-evaluating Old Data with New AI Perspective
1.  Update your AI Expert Prompt in `config.yaml`.
2.  Run: `python main.py summarize --force`.
3.  This triggers new summary creation, which the `monitor` (if running) will immediately pick up and re-evaluate using the new prompt.

---

## 5. Error Codes & Diagnostics
- **Exit Code 0**: Success.
- **Exit Code 1**: General Error (Check stdout/stderr).
- **"Skipping {id}"**: Item already exists (normal optimization).
- **"Error: Raw directory ... does not exist"**: Occurs when using `--dir` with an invalid path.

## 6. Best Practices for AI Agents
- **Token Management**: Always use `--skip-existing` and avoid `--force` unless prompts have changed.
- **Encoding**: The system uses `UTF-8`. Ensure your environment variables `PYTHONIOENCODING=utf-8` are set on Windows.
- **Rate Limiting**: The system includes a 1-second sleep between items. Do not remove this to prevent IP bans from HN or Rate Limits from LLM providers.
