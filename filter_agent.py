import os
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


def strip_thinking_tags(text):
    """Kept as a safety net in case a future model swap reintroduces reasoning tags."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def filter_articles(articles, top_k=5):
    if not articles:
        return []
    
    article_text = "\n\n".join([
        f"[{i+1}] Source: {a['source']}\nTitle: {a['title']}\nURL: {a['url']}"
        for i, a in enumerate(articles)
    ])
    
    prompt = f"""You are a tech news curator. Evaluate these {len(articles)} articles.

Score each on THREE dimensions (1-10 each):
1. ARCHITECTURE_IMPACT: How much does this change how systems are designed/built?
2. MARKET_IMPACT: Business implications? Hiring/competition changes?
3. JOB_IMPACT: How relevant is this to what engineers need to know?

Return ONLY a valid JSON array with the top {top_k} DISTINCT articles (no duplicates, no repeated titles). No explanation, no markdown, just the JSON array:
[
  {{
    "rank": 1,
    "title": "article title",
    "url": "article url",
    "source": "source name",
    "architecture_impact": 8,
    "market_impact": 6,
    "job_impact": 7,
    "reason": "brief explanation of why this matters"
  }}
]

ARTICLES TO EVALUATE:
{article_text}"""
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        print(f"✗ Error {response.status_code}: {response.text[:300]}")
        return []
    
    raw_content = response.json()["choices"][0]["message"]["content"]
    cleaned = strip_thinking_tags(raw_content)
    
    if '```json' in cleaned:
        cleaned = cleaned.split('```json')[1].split('```')[0]
    elif '```' in cleaned:
        cleaned = cleaned.split('```')[1].split('```')[0]
    
    if '[' in cleaned:
        cleaned = cleaned[cleaned.find('['):cleaned.rfind(']')+1]
    
    parsed = json.loads(cleaned.strip())
    
    seen_titles = set()
    deduped = []
    for article in parsed:
        if article['title'] not in seen_titles:
            seen_titles.add(article['title'])
            deduped.append(article)
    
    return deduped


if __name__ == "__main__":
    from scraper import get_all_articles
    
    print("Scraping...")
    articles = get_all_articles()
    print(f"✓ Got {len(articles)} articles\n")
    
    print("Filtering via Groq...")
    filtered = filter_articles(articles, top_k=5)
    
    print(f"\n✓ Top {len(filtered)} articles:\n")
    for a in filtered:
        print(f"[{a['rank']}] {a['title']}")
        print(f"    Arch: {a.get('architecture_impact')} | Market: {a.get('market_impact')} | Job: {a.get('job_impact')}")
        print(f"    Why: {a.get('reason')}\n")