receipt_last_year_resilient = """
import streamlit as st
import zipfile
import json
import os
from collections import Counter
from datetime import datetime, timedelta
import tempfile

st.set_page_config(page_title="Kickback: Last Year", page_icon="🧾")
st.title("🧾 Kickback: Your Last Year on YouTube")

st.write("Upload your Google Takeout ZIP — we’ll generate a receipt based only on your past 12 months of YouTube activity.")

CUTOFF_DATE = datetime.utcnow() - timedelta(days=365)

def generate_watch_summary(data, value_per_view=0.08):
    watched_titles = []
    watch_hours = []
    for item in data:
        if 'title' in item and item['title'].startswith("Watched ") and 'time' in item:
            try:
                dt = datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
                if dt >= CUTOFF_DATE:
                    watched_titles.append(item['title'].replace("Watched ", "").strip())
                    watch_hours.append(dt.hour)
            except:
                continue
    total_videos = len(watched_titles)
    estimated_value = round(total_videos * value_per_view, 2)
    top_titles = Counter(watched_titles).most_common(3)
    most_active_hour = Counter(watch_hours).most_common(1)
    most_active_hour = f"{most_active_hour[0][0]}:00" if most_active_hour else "N/A"
    return {
        "total_videos": total_videos,
        "estimated_value": f"${estimated_value:.2f}",
        "top_titles": [title for title, _ in top_titles],
        "most_active_hour": most_active_hour
    }

def parse_youtube_search_history(data, value_per_search=0.03):
    searches = []
    for item in data:
        if 'title' in item and item['title'].startswith("Searched for ") and 'time' in item:
            try:
                dt = datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
                if dt >= CUTOFF_DATE:
                    searches.append(item['title'].replace("Searched for ", "").strip())
            except:
                continue
    total_searches = len(searches)
    estimated_value = round(total_searches * value_per_search, 2)
    top_searches = Counter(searches).most_common(3)
    return {
        "total_searches": total_searches,
        "estimated_value": f"${estimated_value:.2f}",
        "top_searches": [term for term, _ in top_searches]
    }

def display_receipt(watch_summary, search_summary):
    total_value = round(
        float(watch_summary['estimated_value'].strip('$')) +
        float(search_summary['estimated_value'].strip('$')),
        2
    )

    top_titles = "\\n".join(f"  • {t}" for t in watch_summary['top_titles']) or "  • (no data)"
    top_terms = "\\n".join(f"  • {t}" for t in search_summary['top_searches']) or "  • (no data)"

    receipt = f\"\"\"
🧾 KICKBACK DATA RECEIPT
📆 Filter: Last 12 Months
----------------------------------------

📺 YOUTUBE WATCH HISTORY

Videos Watched      {watch_summary['total_videos']}
Most Active Hour    {watch_summary['most_active_hour']}

Top Watched Titles:
{top_titles}

Ad Value Generated  {watch_summary['estimated_value']}

----------------------------------------

🔍 YOUTUBE SEARCH HISTORY

Searches Made       {search_summary['total_searches']}

Top Search Terms:
{top_terms}

Ad Value Generated  {search_summary['estimated_value']}

----------------------------------------

💰 SUMMARY

Total Value to Google  ${total_value:.2f}
You Received           $0.00 😐

They watched you watch.  
Time to take your data back.
\"\"\"

    st.text(receipt)

zip_file = st.file_uploader("Upload your Google Takeout .zip", type="zip")

if zip_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_file, "r") as z:
            z.extractall(tmpdir)

        watch_path = None
        search_path = None

        for root, _, files in os.walk(tmpdir):
            for f in files:
                if f == "watch-history.json":
                    watch_path = os.path.join(root, f)
                elif f == "search-history.json":
                    search_path = os.path.join(root, f)

        if watch_path and search_path:
            with open(watch_path, 'r', encoding='utf-8') as f:
                watch_data = json.load(f)
            with open(search_path, 'r', encoding='utf-8') as f:
                search_data = json.load(f)

            watch_summary = generate_watch_summary(watch_data)
            search_summary = parse_youtube_search_history(search_data)

            display_receipt(watch_summary, search_summary)
        else:
            st.error("Could not find both `watch-history.json` and `search-history.json` in your .zip file. Make sure your Takeout includes YouTube history.")
"""

resilient_filtered_path = "/mnt/data/kickback_streamlit_last_year_resilient.py"
with open(resilient_filtered_path, "w") as f:
    f.write(receipt_last_year_resilient.strip())

resilient_filtered_path
Result
'/mnt/data/kickback_streamlit_last_year_resilient.py'
