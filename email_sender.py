import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# Toggle: "true" sends to every address in RECIPIENT_EMAIL (comma-separated),
# anything else (or unset) sends to just the first address — fails safely toward "one recipient."
MULTI_RECIPIENT_MODE = os.getenv("MULTI_RECIPIENT_MODE", "false").strip().lower() == "true"
_raw_recipients = os.getenv("RECIPIENT_EMAIL", "").strip().split(",")
_raw_recipients = [email.strip() for email in _raw_recipients if email.strip()]

RECIPIENT_EMAILS = _raw_recipients if MULTI_RECIPIENT_MODE else _raw_recipients[:1]

def format_email_body(filtered_articles, summary):
    date_str = datetime.now().strftime("%B %d, %Y")
    
    def impact_color(score):
        """Color-code impact badges based on score."""
        if score >= 8:
            return "#e74c3c"  # high impact - red/orange
        elif score >= 6:
            return "#f39c12"  # medium impact - amber
        else:
            return "#95a5a6"  # lower impact - grey
    
    # Build summary bullets as styled list items instead of a raw paragraph
    summary_lines = [line.strip().lstrip("- ").strip() for line in summary.split("\n") if line.strip()]
    summary_html = "".join([
        f"""
        <li style="margin-bottom: 14px; padding-left: 0; list-style: none; display: flex; align-items: flex-start;">
            <span style="flex-shrink: 0; color: #1a1a2e; font-size: 15px; font-weight: 700; 
                         margin-right: 10px; min-width: 18px;">
                {i+1}.
            </span>
            <span style="line-height: 1.5;">{line}</span>
        </li>
        """
        for i, line in enumerate(summary_lines)
    ])
    
    # Build article cards
    articles_html = ""
    for a in filtered_articles:
        arch = a.get('architecture_impact', 0)
        market = a.get('market_impact', 0)
        job = a.get('job_impact', 0)
        
        articles_html += f"""
        <div style="background: #ffffff; border: 1px solid #e8e8e8; border-radius: 10px; 
                    padding: 18px 20px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
            <a href="{a['url']}" style="color: #1a1a2e; text-decoration: none; font-size: 16px; font-weight: 600; line-height: 1.4;">
                {a['title']}
            </a>
            <div style="margin-top: 10px; font-size: 12px; color: #888;">
                📍 {a['source']}
            </div>
            <div style="margin-top: 12px;">
                <span style="display: inline-block; background: {impact_color(arch)}15; color: {impact_color(arch)}; 
                             padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; margin-right: 6px;">
                    Architecture {arch}/10
                </span>
                <span style="display: inline-block; background: {impact_color(market)}15; color: {impact_color(market)}; 
                             padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; margin-right: 6px;">
                    Market {market}/10
                </span>
                <span style="display: inline-block; background: {impact_color(job)}15; color: {impact_color(job)}; 
                             padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">
                    Job {job}/10
                </span>
            </div>
        </div>
        """
    
    html = f"""
    <html>
    <body style="font-family: -apple-system, 'Segoe UI', Roboto, Arial, sans-serif; 
                 background: #f4f5f7; margin: 0; padding: 24px 12px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; 
                    border-radius: 16px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06);">
            
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 32px 28px;">
                <div style="font-size: 22px; font-weight: 700; color: #ffffff;">🎯 TRACE</div>
                <div style="font-size: 13px; color: #a8a8c0; margin-top: 4px;">{date_str}</div>
            </div>
            
            <div style="padding: 28px;">
                <p style="font-size: 15px; color: #333; margin: 0 0 20px 0;">
                    Good morning Rei☀️ — here's what mattered in tech today.
                </p>
                
                <ul style="padding: 0; margin: 0 0 28px 0; font-size: 14px; color: #333; line-height: 1.6;">
                    {summary_html}
                </ul>
                
                <div style="font-size: 13px; font-weight: 700; color: #888; text-transform: uppercase; 
                            letter-spacing: 0.5px; margin-bottom: 14px;">
                    Top Stories
                </div>
                
                {articles_html}
            </div>
            
            <div style="padding: 20px 28px; background: #fafafa; border-top: 1px solid #eee; 
                        text-align: center; font-size: 12px; color: #aaa;">
                Curated automatically by TRACE • Scrape → Filter → Summarize → Deliver
            </div>
        </div>
    </body>
    </html>
    """
    return html



def send_digest(filtered_articles, summary):
    message = MIMEMultipart("alternative")
    message["Subject"] = f"📰 Daily Tech News - {datetime.now().strftime('%b %d, %Y')}"
    message["From"] = SENDER_EMAIL
    message["To"] = ", ".join(RECIPIENT_EMAILS)
    
    html_body = format_email_body(filtered_articles, summary)
    message.attach(MIMEText(html_body, "html"))
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAILS, message.as_string())
    
    print(f"✓ Email sent to {len(RECIPIENT_EMAILS)} recipients")


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
