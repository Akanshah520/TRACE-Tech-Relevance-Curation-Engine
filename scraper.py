import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_hacker_news(limit=15):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get("https://news.ycombinator.com", headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    rows = soup.find_all('tr', class_='athing')[:limit]
    
    for row in rows:
        title_elem = row.find('span', class_='titleline')
        if title_elem and title_elem.find('a'):
            title = title_elem.find('a').text
            url = title_elem.find('a').get('href', '')
            if url.startswith('http'):
                articles.append({
                    'source': 'Hacker News',
                    'title': title,
                    'url': url,
                    'timestamp': datetime.now().isoformat()
                })
    
    return articles


def scrape_arxiv_ai(limit=10):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get("https://arxiv.org/list/cs.AI/recent", headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    entries = soup.find_all('dt')[:limit]
    
    for entry in entries:
        next_dd = entry.find_next('dd')
        if next_dd:
            title_div = next_dd.find('div', class_='list-title')
            if title_div:
                title = title_div.text.replace('Title:', '').strip()
                arxiv_link = entry.find('a', title='Abstract')
                if arxiv_link:
                    url = f"https://arxiv.org{arxiv_link.get('href')}"
                    articles.append({
                        'source': 'arXiv AI',
                        'title': title[:100],
                        'url': url,
                        'timestamp': datetime.now().isoformat()
                    })
    
    return articles


def get_all_articles():
    all_articles = []
    all_articles.extend(scrape_hacker_news(limit=15))
    all_articles.extend(scrape_arxiv_ai(limit=10))
    return all_articles


if __name__ == "__main__":
    articles = get_all_articles()
    print(f"✓ Found {len(articles)} total articles\n")
    
    for a in articles:
        print(f"[{a['source']}] {a['title'][:70]}")