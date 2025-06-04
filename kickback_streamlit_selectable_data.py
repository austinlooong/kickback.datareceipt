import streamlit as st
import zipfile
import json
import os
from collections import Counter
from datetime import datetime
import tempfile

st.set_page_config(page_title="Kickback (Custom Data)", page_icon="🧾")
st.title("🧾 Kickback: Upload Your Google Takeout .zip")

st.markdown("Upload your Google Takeout ZIP file and choose what kind of data receipt you'd like to generate.")

# Data options
data_options = st.multiselect(
    "Which data types would you like to include?",
    ["YouTube Watch History", "YouTube Search History", "Google Search History", "Location History"],
    default=["YouTube Watch History", "YouTube Search History"]
)

# --- Data parsing functions ---

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

def format_section(header, lines):
    return "\n".join([f"{header}", "-" * len(header)] + lines + [""])

# --- Upload & Process ZIP ---

zip_file = st.file_uploader("Upload your Google Takeout .zip", type="zip")

if zip_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_file, "r") as z:
            z.extractall(tmpdir)

        found_files = {
            "YouTube Watch History": None,
            "YouTube Search History": None,
            "Google Search History": None,
            "Location History": None
        }

        for root, _, files in os.walk(tmpdir):
            for f in files:
                if f == "watch-history.json":
                    found_files["YouTube Watch History"] = os.path.join(root, f)
                elif f == "search-history.json":
                    found_files["YouTube Search History"] = os.path.join(root, f)
                elif f == "MyActivity.json":
                    found_files["Google Search History"] = os.path.join(root, f)
                elif f in ("Semantic Location History.json", "Location History.json"):
                    found_files["Location History"] = os.path.join(root, f)

        receipt = ["🧾 KICKBACK DATA RECEIPT", "------------------------------"]

        total_value = 0.0

        if "YouTube Watch History" in data_options and found_files["YouTube Watch History"]:
            with open(found_files["YouTube Watch History"], 'r', encoding='utf-8') as f:
                data = json.load(f)
                summary = generate_watch_summary(data)
                total_value += float(summary["estimated_value"].strip('$'))
                section = [
                    f"Videos Watched: {summary['total_videos']}",
                    f"Value Generated: {summary['estimated_value']}",
                    f"Most Active Hour: {summary['most_active_hour']}",
                    "Top Titles:"
                ] + [f"  - {t}" for t in summary['top_titles']]
                receipt.append(format_section("📺 YouTube Watch", section))

        if "YouTube Search History" in data_options and found_files["YouTube Search History"]:
            with open(found_files["YouTube Search History"], 'r', encoding='utf-8') as f:
                data = json.load(f)
                summary = parse_youtube_search_history(data)
                total_value += float(summary["estimated_value"].strip('$'))
                section = [
                    f"Searches: {summary['total_searches']}",
                    f"Value Generated: {summary['estimated_value']}",
                    "Top Searches:"
                ] + [f"  - {s}" for s in summary['top_searches']]
                receipt.append(format_section("🔍 YouTube Search", section))

        if "Google Search History" in data_options and found_files["Google Search History"]:
            with open(found_files["Google Search History"], 'r', encoding='utf-8') as f:
                data = json.load(f)
                summary = parse_google_search_history(data)
                total_value += float(summary["estimated_value"].strip('$'))
                section = [
                    f"Searches: {summary['total_google_searches']}",
                    f"Value Generated: {summary['estimated_value']}",
                    "Top Queries:"
                ] + [f"  - {s}" for s in summary['top_google_searches']]
                receipt.append(format_section("🌐 Google Search", section))

        if "Location History" in data_options and found_files["Location History"]:
            with open(found_files["Location History"], 'r', encoding='utf-8') as f:
                data = json.load(f)
                summary = parse_location_history(data)
                total_value += float(summary["estimated_value"].strip('$'))
                section = [
                    f"Pings Logged: {summary['total_locations']}",
                    f"Value Generated: {summary['estimated_value']}"
                ]
                receipt.append(format_section("📍 Location History", section))

        receipt.append("------------------------------")
        receipt.append(f"💰 Total Value to Google: ${round(total_value, 2)}")
        receipt.append("You Received:            $0.00 😐")
        receipt.append("")
        receipt.append("They watched you watch.")
        receipt.append("Time to take your data back.")

        st.markdown("<pre style='background:#f4f4f4;padding:1.5rem;border:1px dashed #bbb;font-family:monospace;white-space:pre-wrap'>" + "\n".join(receipt) + "</pre>", unsafe_allow_html=True)