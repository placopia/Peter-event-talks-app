# BigQuery Release Notes Hub 📊🐦

A premium, modern web dashboard built with **Python Flask** and **Vanilla HTML, CSS, and JavaScript**. This application aggregates, parses, and visualizes the official Google Cloud BigQuery release notes feed. It includes dynamic searching, real-time category filtering, and an interactive X/Twitter composer drawer for one-click sharing.

---

## ✨ Features

*   **Smart Parsing Engine**: Segmentizes daily Google Cloud RSS updates into granular, itemized release cards (Features, Changes, Issues, Deprecations).
*   **Performance Cache**: Implements an in-memory server-side cache (15-minute lifespan) to reduce latency and feed retrieval overhead.
*   **Fuzzy Searching**: Filter updates instantly by keywords, dates, or categories client-side.
*   **Interactive Tweet Composer**: Click on any update card to draft a tweet. Automatically structures the content, handles smart truncation, and provides a real-time character limit circular progress ring.
*   **Premium Dark UI**: Features a custom dark-mode theme built with CSS variables, responsive side drawers, and subtle glassmorphic finishes.

---

## 🛠️ Tech Stack

*   **Backend**: Python 3.11, Flask
*   **Feed Parser**: `feedparser`, `BeautifulSoup4`
*   **Frontend**: Vanilla HTML5, Vanilla CSS3 (Custom Grid & Flexbox), ES6 JavaScript
*   **Icons & Fonts**: FontAwesome v6, Outfit (Google Fonts)

---

## 📂 Project Structure

```
C:/Users/Peter/agy-cli-projects/
├── bq_release_notes/
│   ├── app.py                # Flask Backend API & Server
│   ├── templates/
│   │   └── index.html        # Main HTML layout
│   └── static/
│       ├── css/
│       │   └── style.css     # Premium UI theme stylesheet
│       └── js/
│           └── main.js       # Search, filter, & composer script
├── .gitignore                # Config to ignore local data and caches
└── README.md                 # Project Documentation
```

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3.x installed.

### 1. Clone & Navigate
```bash
git clone https://github.com/placopia/Peter-event-talks-app.git
cd Peter-event-talks-app/bq_release_notes
```

### 2. Install Dependencies
Install the required packages using pip:
```bash
pip install flask feedparser beautifulsoup4 requests
```

### 3. Run the Server
Launch the Flask development server:
```bash
python app.py
```
By default, the server will start at **`http://127.0.0.1:5000`**.

---

## 💻 Usage & Workflows

### 🔄 Refresh Feed
The feed is loaded dynamically from the cache on page load. To bypass the cache and force a fresh fetch from the Google Cloud server, click the **Sync Notes** button in the sidebar.

### 🔍 Filter & Search
*   Use the **Search Bar** in the sidebar to search for keywords (e.g. `Gemini`, `Studio`, `continuous queries`).
*   Click the **Category Buttons** to filter updates by *Features*, *Changes*, *Issues*, *Deprecations*, or *General Info*.

### 🐦 Tweet Composer
1.  Click on any release card.
2.  The **Tweet Composer Drawer** will slide open on the right.
3.  Modify the tweet text inside the editor. The circular progress ring will change color:
    *   🟢 **Green**: Code is safe.
    *   🟡 **Amber**: Approaching limit (<= 40 characters remaining).
    *   🔴 **Red**: Exceeded 280 characters (disables posting).
4.  Click **Post Tweet** to open the Twitter Web Share Intent directly.
