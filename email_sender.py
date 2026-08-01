import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


def format_email_body(filtered_articles, summary):
    date_str = datetime.now().strftime("%B %d, %Y")
    
    articles_html = "<h3>📌 Top Articles</h3><ul>"
    for a in filtered_articles:
        articles_html += (
            f"<li><strong><a href='{a['url']}'>{a['title']}</a></strong>"
            f"<br/><small>{a['source']} | Arch: {a.get('architecture_impact', 0)}/10 "
            f"| Market: {a.get('market_impact', 0)}/10 "
            f"| Job: {a.get('job_impact', 0)}/10</small></li>")
    articles_html += "</ul>"
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1>🤖 Tech News Digest</h1>
        <p><strong>Date:</strong> {date_str}</p>
        <div style="background: #f0f7ff; padding: 20px; border-left: 4px solid #0066cc; margin: 20px 0;">
            <h2>Today's Briefing</h2>
            <p>{summary.replace(chr(10), '<br/>')}</p>
        </div>
        {articles_html}
        <hr/>
        <p style="color: #999; font-size: 12px;">Autonomous Tech News Agent</p>
    </body>
    </html>
    """
    return html


def send_digest(filtered_articles, summary):
    message = MIMEMultipart("alternative")
    message["Subject"] = f"📰 Daily Tech News - {datetime.now().strftime('%b %d, %Y')}"
    message["From"] = SENDER_EMAIL
    message["To"] = RECIPIENT_EMAIL
    
    html_body = format_email_body(filtered_articles, summary)
    message.attach(MIMEText(html_body, "html"))
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())
    
    print(f"✓ Email sent to {RECIPIENT_EMAIL}")


if __name__ == "__main__":
    from scraper import get_all_articles
    from filter_agent import filter_articles
    from summarizer import summarize_articles
    
    print("Scraping...")
    articles = get_all_articles()
    
    print("Filtering...")
    filtered = filter_articles(articles, top_k=5)
    
    print("Summarizing...")
    summary = summarize_articles(filtered)
    
    print("Sending email...")
    send_digest(filtered, summary)