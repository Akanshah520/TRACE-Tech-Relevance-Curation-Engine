import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


def strip_thinking_tags(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def summarize_articles(filtered_articles):
    if not filtered_articles:
        return "No articles to summarize."
    
    article_lines = "\n".join([
        f"- {a['title']} (Architecture: {a.get('architecture_impact', 0)}/10, "
        f"Market: {a.get('market_impact', 0)}/10, Job: {a.get('job_impact', 0)}/10) "
        f"— {a.get('reason', '')}"
        for a in filtered_articles
    ])
    
    prompt = f"""Summarize the following tech news into EXACTLY 5 bullet points.

Rules:
- Each bullet is ONE sentence
- Focus on why it matters (architecture, market, or job impact)
- No intro text, no closing remarks, no headers
- Output ONLY the bullet points, starting each with "- "

News:
{article_lines}

Bullet summary:"""
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        print(f"✗ Error {response.status_code}: {response.text[:300]}")
        return ""
    
    raw_content = response.json()["choices"][0]["message"]["content"]
    return strip_thinking_tags(raw_content)


if __name__ == "__main__":
    from scraper import get_all_articles
    from filter_agent import filter_articles
    
    print("Scraping...")
    articles = get_all_articles()
    print(f"✓ Got {len(articles)} articles\n")
    
    print("Filtering...")
    filtered = filter_articles(articles, top_k=5)
    print(f"✓ Filtered to {len(filtered)} articles\n")
    
    print("Summarizing via Groq...")
    summary = summarize_articles(filtered)
    
    print("\n" + "=" * 60)
    print(summary)
    print("=" * 60)