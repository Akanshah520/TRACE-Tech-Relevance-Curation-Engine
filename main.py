from scraper import get_all_articles
from filter_agent import filter_articles
from summarizer import summarize_articles
from email_sender import send_digest


def run_pipeline():
    print("🤖 Starting TRACE pipeline...\n")

    print("[1/4] Scraping...")
    articles = get_all_articles()
    print(f"  → {len(articles)} articles found\n")

    print("[2/4] Filtering...")
    filtered = filter_articles(articles, top_k=5)
    print(f"  → {len(filtered)} top articles selected\n")

    print("[3/4] Summarizing...")
    summary = summarize_articles(filtered)
    print(f"  → Summary generated\n")

    print("[4/4] Sending email...")
    send_digest(filtered, summary)

    print("\n✓ TRACE run complete.")


if __name__ == "__main__":
    run_pipeline()