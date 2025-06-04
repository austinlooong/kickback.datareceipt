import streamlit as st
import zipfile
import json
import os
from collections import Counter
from datetime import datetime
import tempfile

st.set_page_config(page_title="Kickback Receipt", page_icon="🧾")
st.title("🧾 Kickback: Upload Your Google Takeout .zip")

st.write("We’ll turn your YouTube activity into a clean, ad-value receipt. Just drop in your Takeout .zip.")

def generate_watch_summary(data, value_per_view=0.08):
    watched_titles = []
    watch_hours = []
    for item in data:
        if 'title' in item and item['title'].startswith("Watched "):
            watched_titles.append(item['title'].replace("Watched ", "").strip())
            if 'time' in item:
                try:
                    dt = datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
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
        if 'title' in item and item['title'].startswith("Searched for "):
            searches.append(item['title'].replace("Searched for ", "").strip())
    total_searches = len(searches)
    estimated_value = round(total_searches * value_per_search, 2)
    top_searches = Counter(searches).most_common(3)
    return {
        "total_searches": total_searches,
        "estimated_value": f"${estimated_value:.2f}",
        "top_searches": [term for term, _ in top_searches]
    }

def format_clean_receipt(watch, yt_search):
    receipt = []
    receipt.append("🧾 KICKBACK DATA RECEIPT")
    receipt.append("----------------------------------------")
    receipt.append("")
    receipt.append("📺 YOUTUBE WATCH HISTORY")
    receipt.append("")
    receipt.append(f"Videos Watched      {watch['total_videos']}")
    receipt.append(f"Most Active Hour    {watch['most_active_hour']}")
    receipt.append("")
    receipt.append("Top Watched:")
    for title in watch['top_titles']:
        receipt.append(f"  • {title}")
    receipt.append("")
    receipt.append(f"Ad Value Generated  {watch['estimated_value']}")
    receipt.append("")
    receipt.append("----------------------------------------")
    receipt.append("")
    receipt.append("🔍 YOUTUBE SEARCH HISTORY")
    receipt.append("")
    receipt.append(f"Searches Made       {yt_search['total_searches']}")
    receipt.append("")
    receipt.append("Top Searches:")
    for term in yt_search['top_searches']:
        receipt.append(f"  • {term}")
    receipt.append("")
    receipt.append(f"Ad Value Generated  {yt_search['estimated_value']}")
    receipt.append("")
    total = sum(float(val['estimated_value'].strip('$')) for val in [watch, yt_search])
    receipt.append("----------------------------------------")
    receipt.append("")
    receipt.append("💰 SUMMARY")
    receipt.append("")
    receipt.append(f"Total Value to Google  ${total:.2f}")
    receipt.append("You Received           $0.00 😐")
    receipt.append("")
    receipt.append("They watched you watch.")
    receipt.append("Time to take your data back.")
    return "\n".join(receipt)

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

            receipt = format_clean_receipt(watch_summary, search_summary)
            st.markdown("<pre style='background:#ffffff;padding:1.5rem;border:1px dashed #bbb;font-family:monospace;font-size:15px;white-space:pre-wrap'>" + receipt + "</pre>", unsafe_allow_html=True)
        else:
            st.error("Could not find both `watch-history.json` and `search-history.json` in your .zip file. Make sure your Takeout includes YouTube history.")