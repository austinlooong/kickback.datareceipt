import streamlit as st
import zipfile
import json
import os
from collections import Counter
from datetime import datetime
import tempfile

st.set_page_config(page_title="Kickback (Full ZIP Parser)", page_icon="🧾")
st.title("🧾 Kickback: Upload Your Google Takeout .zip")
st.write("Drop your full Google Takeout .zip here. We’ll scan for YouTube, Google Search, and Location data to generate your ad value receipt.")

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
    top_titles = Counter(watched_titles).most_common(5)
    most_active_hour = Counter(watch_hours).most_common(1)
    most_active_hour = f"{most_active_hour[0][0]}:00" if most_active_hour else "N/A"
    return {
        "total_videos": total_videos,
        "estimated_value": f"${estimated_value}",
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
    top_searches = Counter(searches).most_common(5)
    return {
        "total_searches": total_searches,
        "estimated_value": f"${estimated_value}",
        "top_searches": [term for term, _ in top_searches]
    }

def parse_google_search_history(data, value_per_search=0.03):
    searches = []
    for item in data.get("event", []):
        for sub in item.get("subEvent", []):
            if "query" in sub:
                searches.append(sub["query"])
    total = len(searches)
    value = round(total * value_per_search, 2)
    top_searches = Counter(searches).most_common(5)
    return {
        "total_google_searches": total,
        "estimated_value": f"${value}",
        "top_google_searches": [term for term, _ in top_searches]
    }

def parse_location_history(data, value_per_ping=0.01):
    count = len(data.get("locations", []))
    value = round(count * value_per_ping, 2)
    return {
        "total_locations": count,
        "estimated_value": f"${value}"
    }

def format_receipt(watch, yt_search, g_search, loc):
    receipt = []
    receipt.append("🧾 KICKBACK DATA RECEIPT")
    receipt.append("----------------------------------")
    receipt.append("📺 YouTube Watch History")
    receipt.append(f"Total Videos Watched: {watch['total_videos']}")
    receipt.append(f"Ad Value Generated:   {watch['estimated_value']}")
    receipt.append(f"Most Active Hour:     {watch['most_active_hour']}")
    receipt.append("Top Watched Titles:")
    for title in watch['top_titles']:
        receipt.append(f"  - {title}")
    receipt.append("")
    receipt.append("🔍 YouTube Search History")
    receipt.append(f"Total Searches:       {yt_search['total_searches']}")
    receipt.append(f"Ad Value Generated:   {yt_search['estimated_value']}")
    receipt.append("Top Search Terms:")
    for term in yt_search['top_searches']:
        receipt.append(f"  - {term}")
    receipt.append("")
    receipt.append("🌐 Google Search History")
    receipt.append(f"Total Searches:       {g_search['total_google_searches']}")
    receipt.append(f"Ad Value Generated:   {g_search['estimated_value']}")
    receipt.append("Top Search Terms:")
    for term in g_search['top_google_searches']:
        receipt.append(f"  - {term}")
    receipt.append("")
    receipt.append("📍 Location History")
    receipt.append(f"Location Pings:       {loc['total_locations']}")
    receipt.append(f"Ad Value Generated:   {loc['estimated_value']}")
    receipt.append("")
    total = sum(float(val['estimated_value'].strip('$')) for val in [watch, yt_search, g_search, loc])
    receipt.append("----------------------------------")
    receipt.append("💰 Summary")
    receipt.append(f"Total Value to Google: ${round(total, 2)}")
    receipt.append("You Received:          $0.00 😐")
    receipt.append("")
    receipt.append("They watched you watch.")
    receipt.append("Time to take your data back.")
    return "\n".join(receipt)

zip_file = st.file_uploader("Upload your Google Takeout .zip", type="zip")

if zip_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_file, "r") as z:
            z.extractall(tmpdir)

        paths = {
            "watch": None,
            "yt_search": None,
            "g_search": None,
            "location": None
        }

        for root, _, files in os.walk(tmpdir):
            for f in files:
                if f == "watch-history.json":
                    paths["watch"] = os.path.join(root, f)
                elif f == "search-history.json":
                    paths["yt_search"] = os.path.join(root, f)
                elif f == "MyActivity.json":
                    paths["g_search"] = os.path.join(root, f)
                elif f in ("Semantic Location History.json", "Location History.json"):
                    paths["location"] = os.path.join(root, f)

        if all(paths.values()):
            with open(paths["watch"], 'r', encoding='utf-8') as f:
                watch_data = json.load(f)
            with open(paths["yt_search"], 'r', encoding='utf-8') as f:
                yt_search_data = json.load(f)
            with open(paths["g_search"], 'r', encoding='utf-8') as f:
                g_search_data = json.load(f)
            with open(paths["location"], 'r', encoding='utf-8') as f:
                location_data = json.load(f)

            receipt = format_receipt(
                generate_watch_summary(watch_data),
                parse_youtube_search_history(yt_search_data),
                parse_google_search_history(g_search_data),
                parse_location_history(location_data)
            )
            st.markdown("<pre style='background:#f4f4f4;padding:1.5rem;border:1px dashed #bbb;font-family:monospace;white-space:pre-wrap'>" + receipt + "</pre>", unsafe_allow_html=True)
        else:
            st.error("Couldn’t find all required files. Make sure your ZIP includes YouTube watch/search, Google search, and location history.")