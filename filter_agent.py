import os
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "openai/gpt-oss-120b:cerebras"


def strip_thinking_tags(text):
    """DeepSeek-R1 wraps its reasoning in <think>...</think> before the real answer.
    We only want what comes after."""
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

Return ONLY a valid JSON array with the top {top_k} DISTINCT articles (no duplicates, no repeated titles). No explanation, no markdown, just the JSON array:[
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
    
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
    
    if response.status_code != 200:
        print(f"✗ Error {response.status_code}: {response.text[:300]}")
        return []
    
    raw_content = response.json()["choices"][0]["message"]["content"]
    cleaned = strip_thinking_tags(raw_content)
    
    # Handle markdown code fences if present
    if '```json' in cleaned:
        cleaned = cleaned.split('```json')[1].split('```')[0]
    elif '```' in cleaned:
        cleaned = cleaned.split('```')[1].split('```')[0]
    
    # Extract just the JSON array portion
    if '[' in cleaned:
        cleaned = cleaned[cleaned.find('['):cleaned.rfind(']')+1]
    
    parsed = json.loads(cleaned.strip())
    
    # Safety net: de-duplicate by title, in case the model repeats itself
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
    print(f" Got {len(articles)} articles\n")
    
    print("Filtering (this may take 10-20 seconds - reasoning models think before answering)...")
    filtered = filter_articles(articles, top_k=5)
    
    print(f"\n✓ Top {len(filtered)} articles:\n")
    for a in filtered:
        print(f"[{a['rank']}] {a['title']}")
        print(f"    Arch: {a.get('architecture_impact')} | Market: {a.get('market_impact')} | Job: {a.get('job_impact')}")
        print(f"    Why: {a.get('reason')}\n")