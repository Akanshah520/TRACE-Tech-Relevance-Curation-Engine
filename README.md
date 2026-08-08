<div align="center">

# 🎯 TRACE
### Tech Relevance & Curation Engine

*A fully automated pipeline that scrapes, scores, and summarizes daily tech news — delivered to your inbox every morning, for $0/month.*



</div>

---

## 📌 The Problem

Tech news moves faster than anyone can read. Most curation is either heavily paid, algorithmically optimized for clicks rather than substance, or just a firehose of headlines with no filter for what actually matters.

**TRACE** answers a narrower, more useful question every morning: *of everything published today, what would actually change how you build, hire, or think about the industry?*

---

## ⚙️ How It Works

```
┌──────────────┐     ┌───────────────┐     ┌────────────────┐     ┌──────────────┐
│    SCRAPE    │ ──▶ │    FILTER     │ ──▶ │   SUMMARIZE    │ ──▶ │    DELIVER   │
│              │     │               │     │                │     │              │
│  5 sources,  │     │  LLM scores   │     │  LLM condenses │     │  Styled HTML │
│  ~50-55      │     │  every article│     │  the top 5     │     │  digest with │
│  articles/day│     │  on 3 impact  │     │  into 5 tight  │     │  color-coded │
│              │     │  dimensions   │     │  bullets       │     │  impact tags │
└──────────────┘     └───────────────┘     └────────────────┘     └──────────────┘
```

Triggered daily by a **GitHub Actions cron job**  runs entirely on GitHub's infrastructure. No server, no local machine, no manual step. It just shows up.

---

## ✨ Features

- 🔍 **Multi-source aggregation**: Hacker News, arXiv AI, TechCrunch, The Verge, and Ars Technica, scraped and normalized into one unified stream
- 🧠 **Multi-dimensional LLM filtering**: every article is scored 1–10 across three independent axes (**architecture impact**, **market impact**, **job relevance**), not ranked by popularity or recency
- 📉 **~90% noise reduction**: ~50-55 raw articles filtered down to the 5 that actually matter, daily
- ✍️ **Tight, consistent summarization**: 5 bullets, one sentence each, no filler
- 📬 **Designed HTML digest**: card-based layout, color-coded impact badges, not a plain-text dump
- 👥 **Configurable delivery**: toggle between single-recipient and multi-recipient delivery via one environment variable
- ⏰ **Fully unattended automation**: GitHub Actions cron, daily, zero manual triggering required
- 💰 **$0/month**: built entirely on free-tier infrastructure (Groq's free API tier + GitHub Actions' free CI/CD minutes)

---

## 🛠️ Tech Stack

| Layer | Technology | Why This Choice |
|---|---|---|
| Scraping | `requests`, `BeautifulSoup`, `feedparser` | HTML scraping for sources without feeds; RSS parsing for the rest — more stable than scraping raw HTML wherever a feed is available |
| Filtering & Summarization | Groq API (`llama-3.3-70b-versatile`) | Fast, free-tier inference; deliberately *not* a heavyweight reasoning model — ranking and summarization don't need one, and a lighter model returns in seconds instead of timing out |
| Email | Gmail SMTP (`smtplib`) | No third-party email service dependency; secured via app-specific passwords |
| Scheduling | GitHub Actions (`cron`) | Free tier, no server to maintain, runs whether or not any machine of mine is on |
| Secrets | GitHub Encrypted Secrets / local `.env` | Credentials never touch source control, verified via `.gitignore` |

---

## 📂 Project Structure

```
tech_news_agent/
├── .github/
│   └── workflows/
│       └── daily_trace.yml      # Cron schedule + CI/CD pipeline definition
├── scraper.py                    # Stage 1 — pulls & normalizes articles from all 5 sources
├── filter_agent.py                # Stage 2 — LLM scores every article on 3 impact axes
├── summarizer.py                  # Stage 3 — condenses the top 5 into clean bullets
├── email_sender.py                # Stage 4 — builds & sends the styled digest
├── main.py                        # Orchestrates all 4 stages in sequence
├── requirements.txt               # Locked dependency versions
└── .gitignore                     # Excludes .env and venv/ from version control
```

Every stage is independently runnable and testable, `python scraper.py` works standalone, as does every other file. `main.py` is the only thing that chains them together end-to-end.

---

## 🚀 Running It Yourself

### 1. Clone & set up the environment

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
GROQ_API_KEY=your_groq_api_key
SENDER_EMAIL=your_gmail_address
GMAIL_APP_PASSWORD=your_16_char_app_password
RECIPIENT_EMAIL=recipient1@example.com,recipient2@example.com
MULTI_RECIPIENT_MODE=true
```

> **Note:** `GMAIL_APP_PASSWORD` requires 2-Step Verification enabled on your Google account — generate one at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords). Set `MULTI_RECIPIENT_MODE=false` to send only to the first address in `RECIPIENT_EMAIL`.

### 3. Run the full pipeline

```bash
python main.py
```

### 4. Automate it

Add the same values as **Repository Secrets** under `Settings → Secrets and variables → Actions` — see `.github/workflows/daily_trace.yml` for the exact schedule and configuration.

---

## 🧭 Design Decisions & Trade-offs

A project is more than its code, here's the reasoning behind the choices that shaped this one.

**Why not just use the biggest/most capable model available?**
Filtering and summarization here are structured tasks — ranking and condensing, not open-ended reasoning. A large reasoning model was tested first and consistently timed out under the full article load; a lighter, purpose-fit model returns reliable results in a fraction of the time, at zero cost. Matching model size to task complexity, rather than defaulting to "biggest available," was a deliberate call.

**Why migrate inference providers mid-build?**
The original provider's free tier carried a very small monthly credit ceiling, discovered only once real usage patterns were tested — not a hypothetical concern, an actual constraint hit during development. Migrating to a provider with a more generous, request-based free tier solved this without introducing any cost.

**Why RSS feeds over raw HTML scraping wherever possible?**
Raw HTML scraping breaks silently whenever a site redesigns its markup. RSS feeds are structured and meant for exactly this kind of automated consumption — more maintenance-resilient for sources that offer them.

**Why three independent impact scores instead of one relevance score?**
A single "relevance" number collapses distinct signals into one — something can be architecturally significant without being a hiring-market story, or vice versa. Scoring architecture, market, and job impact separately preserves that nuance and makes the *reasoning* behind each pick auditable, not just the ranking.

---

## 🐛 What Went Wrong (And What It Taught)

Real projects break in real ways — a few of the more instructive ones from building this:

- **A third-party API was deprecated mid-development.** The original inference endpoint stopped resolving entirely partway through the build — not a code bug, an entire hosting architecture change on the provider's side. Diagnosed via direct DNS failure investigation rather than assumption, and rebuilt against the new endpoint structure.
- **A reasoning model silently over-engineered a simple task.** Using a large chain-of-thought model for article ranking caused consistent request timeouts — the model was "thinking" through a task that didn't need deep reasoning. Swapping to a lighter, purpose-fit model resolved it in one change.
- **Credentials with invisible whitespace caused two separate authentication failures**, in two different systems (SMTP and an API header), diagnosed both times by isolating the exact byte-length of the loaded value rather than guessing at the cause.

---

## 📊 By the Numbers

| Metric | Value |
|---|---|
| Sources aggregated | 5 |
| Articles processed per run | ~50–55 |
| Articles surfaced per digest | 5 |
| Noise reduction rate | ~90% |
| Monthly infrastructure cost | $0 |
| Manual steps required after deployment | 0 |

---

## 🗺️ Roadmap

- [ ] Weekly "everything that mattered but didn't make the cut" digest, pulling from a rolling historical archive
- [ ] Lightweight faithfulness/verification pass on generated summaries
- [ ] Quantitative quality metrics tracked per run (filter ratio, source diversity, summary consistency)
- [ ] Additional sources via RSS

---

<div align="center">

**Built, broken, debugged, and shipped — one deliberate decision at a time.**

</div>
