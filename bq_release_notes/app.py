import re
import time
import requests
import feedparser
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

FEED_URL = "https://docs.cloud.google.com/feeds/bigquery-release-notes.xml"

# In-memory cache for parsed releases
cache = {
    "data": None,
    "last_updated": 0
}
CACHE_DURATION_SECS = 900  # 15 minutes cache

def clean_text(text):
    # Replace newlines and multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove space before punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    return text.strip()

def generate_suggested_tweet(date, category, content_text, link):
    # Create a clean tweet text that fits 280 characters
    prefix = f"BigQuery Update ({date}) [{category}]: "
    # We will use the base URL for release notes or the specific section anchor
    hashtag_suffix = "\n\n#BigQuery #GoogleCloud #DataEngineering"
    link_suffix = f"\n{link}"
    
    # Calculate available space for content text
    reserved_len = len(prefix) + len(link_suffix) + len(hashtag_suffix)
    available_len = 280 - reserved_len
    
    clean_content = clean_text(content_text)
    if len(clean_content) > available_len:
        # Truncate content text with ellipsis
        clean_content = clean_content[:available_len - 3] + "..."
        
    return f"{prefix}{clean_content}{link_suffix}{hashtag_suffix}"

def fetch_and_parse_feed():
    try:
        response = requests.get(FEED_URL, timeout=10)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        updates = []
        
        for entry_idx, entry in enumerate(feed.entries):
            date_str = entry.title  # e.g., "June 15, 2026"
            updated_str = entry.get('updated', '')
            link = entry.link
            
            # Extract HTML content
            content_html = entry.get('content', [{}])[0].get('value', '') or entry.get('summary', '')
            if not content_html:
                continue
                
            soup = BeautifulSoup(content_html, 'html.parser')
            
            # Loop through soup elements and split by headers
            current_category = "General"
            current_content = []
            
            def save_update(category, content_elements, index):
                if not content_elements:
                    return
                html_text = "".join(str(e) for e in content_elements).strip()
                text_content = BeautifulSoup(html_text, 'html.parser').get_text(separator=' ').strip()
                clean_txt = clean_text(text_content)
                
                # Generate a unique ID
                update_id = f"{entry_idx}_{index}"
                
                # Auto-generate a suggested tweet
                suggested_tweet = generate_suggested_tweet(date_str, category, clean_txt, link)
                
                updates.append({
                    "id": update_id,
                    "date": date_str,
                    "updated": updated_str,
                    "category": category,
                    "content_html": html_text,
                    "content_text": clean_txt,
                    "link": link,
                    "suggested_tweet": suggested_tweet
                })

            sub_update_idx = 0
            for element in soup.contents:
                # Some feeds might put headers in h2 or h3
                if element.name in ['h3', 'h2', 'h4']:
                    save_update(current_category, current_content, sub_update_idx)
                    sub_update_idx += 1
                    current_category = element.get_text().strip()
                    current_content = []
                elif element.name is not None:
                    current_content.append(element)
                    
            # Save final collected section
            save_update(current_category, current_content, sub_update_idx)
            
        return updates
    except Exception as e:
        print(f"Error fetching feed: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/releases')
def get_releases():
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    current_time = time.time()
    
    if force_refresh or cache["data"] is None or (current_time - cache["last_updated"] > CACHE_DURATION_SECS):
        data = fetch_and_parse_feed()
        if data is not None:
            cache["data"] = data
            cache["last_updated"] = current_time
        elif cache["data"] is None:
            # If the fetch fails and we have no cached data, return error
            return jsonify({"error": "Failed to retrieve release notes feed"}), 500
            
    return jsonify({
        "releases": cache["data"],
        "last_updated": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cache["last_updated"]))
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
