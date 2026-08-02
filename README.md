<div align="center">

# 🎯 TRACE
### Tech Relevance & Curation Engine

*An autonomous pipeline that scrapes, scores, and summarizes daily tech news — delivered straight to your inbox at 11 AM, every day, for free.*

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![GitHub Actions](https://img.shields.io/badge/Automated%20via-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![HuggingFace](https://img.shields.io/badge/Powered%20by-HuggingFace%20Inference-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/)
[![Cost](https://img.shields.io/badge/Infra%20Cost-%240%2Fmonth-brightgreen)]()
[![License](https://img.shields.io/badge/License-MIT-lightgrey)]()

</div>

---

## 📌 What This Is

Tech news moves faster than anyone can read. TRACE reads it for you.

Every morning, TRACE scrapes multiple tech news sources, uses an LLM to score each article on **actual impact** — architecture, market, and job relevance — filters out the noise, and emails you a tight 5-bullet briefing with links to the full stories.

No dashboards to check. No newsletters to skim. It just shows up.

---

## ⚙️ How It Works

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐     ┌─────────────┐
│   SCRAPE    │ ──▶ │    FILTER    │ ──▶ │   SUMMARIZE   │ ──▶ │    EMAIL    │
│             │     │              │     │               │     │             │
│ Hacker News │     │ LLM scores   │     │ LLM condenses │     │ HTML digest │
│ arXiv AI    │     │ by impact:   │     │ top 5 into    │     │ w/ links,   │
│ + more soon │     │ Arch/Market/ │     │ 5 clean       │     │ sent via    │
│             │     │ Job (1-10)   │     │ bullets       │     │ Gmail SMTP  │
└─────────────┘     └──────────────┘     └───────────────┘     └─────────────┘
```

Triggered daily by a **GitHub Actions cron job** — runs on GitHub's infrastructure, not your machine. Set it up once, forget it exists, and it just keeps working.

---

## ✨ Features

- 🔍 **Multi-source scraping** — currently Hacker News + arXiv AI, designed to extend to more
- 🧠 **LLM-based relevance filtering** — scores articles on architecture, market, and job impact, not just popularity
- ✍️ **Concise summarization** — 5 bullets, one sentence each, no fluff
- 📬 **HTML email digest** — clean formatting, direct links, impact scores visible per article
- ⏰ **Fully automated** — GitHub Actions cron, runs daily at 11:00 AM IST, zero manual effort
- 💰 **$0/month** — built entirely on free-tier infrastructure (HuggingFace Inference API + GitHub Actions)
- 🧩 **Modular architecture** — each pipeline stage is an independent, testable component

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Scraping | `requests` + `BeautifulSoup` | Lightweight, no headless browser overhead |
| Filtering | HuggingFace Inference API (fast chat model) | Free tier, sub-15s inference, right-sized for a ranking task |
| Summarization | HuggingFace Inference API (same model) | Instruction-following for strict bullet formatting |
| Email | Gmail SMTP (`smtplib`) | Free, secure via app passwords, no extra service dependency |
| Scheduling | GitHub Actions (`cron`) | Free tier, reliable, zero server management |
| Secrets | GitHub Encrypted Secrets / `.env` (local) | Credentials never touch source control |

---

## 📂 Project Structure

```
tech_news_agent/
├── .github/
│   └── workflows/
│       └── daily_trace.yml      # Cron schedule + CI/CD pipeline definition
├── scraper.py                    # Stage 1 — pulls articles from all sources
├── filter_agent.py                # Stage 2 — LLM scores & ranks by impact
├── summarizer.py                  # Stage 3 — condenses top picks into bullets
├── email_sender.py                # Stage 4 — formats & sends the digest
├── main.py                        # Orchestrates all 4 stages in sequence
├── requirements.txt               # Locked dependency versions
└── .gitignore                     # Excludes .env and venv/ from version control
```

Each stage can be run and tested independently — `python scraper.py` works on its own, as does every other file. `main.py` is the only thing that chains them together.

---

## 🚀 Running It Yourself

### 1. Clone & set up environment

```bash
git clone https://github.com/Akanshah520/TRACE-Tech-Relevance-Curation-Engine.git
cd TRACE-Tech-Relevance-Curation-Engine

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### 2. Configure credentials

Create a `.env` file in the project root:

```env
HF_API_TOKEN=your_huggingface_token
SENDER_EMAIL=your_gmail_address
GMAIL_APP_PASSWORD=your_16_char_app_password
RECIPIENT_EMAIL=where_to_send_the_digest
```

> **Note:** `HF_API_TOKEN` needs the *"Make calls to Inference Providers"* fine-grained permission. `GMAIL_APP_PASSWORD` requires 2-Step Verification enabled on your Google account — generate one at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).

### 3. Run the full pipeline

```bash
python main.py
```

### 4. Automate it (optional)

Add the same 4 values as **Repository Secrets** under `Settings → Secrets and variables → Actions`, then GitHub Actions handles the rest — see `.github/workflows/daily_trace.yml`.

---

## 🧭 Design Decisions

A few deliberate choices worth calling out:

- **Free models over premium APIs for filtering/summarization** — these are structured ranking and instruction-following tasks, not tasks that require frontier-model reasoning. A right-sized free model performs comparably at zero cost.
- **Two-stage LLM use (filter → summarize) instead of one monolithic prompt** — keeps each step debuggable and independently testable, and lets the reasoning behind article selection stay transparent (each article carries its own impact scores).
- **GitHub Actions over a paid server** — the entire pipeline runs in well under the free tier's monthly minutes, so scheduling costs nothing.

---

## 🗺️ Roadmap

- [ ] Add more sources (TechCrunch, The Verge, GitHub Trending)
- [ ] Track click-through data to refine filtering criteria over time
- [ ] Store historical digests for trend analysis
- [ ] Slack/Discord delivery option alongside email

---

<div align="center">

**Built with curiosity, a lot of debugging, and zero dollars in infrastructure cost.**

</div>
