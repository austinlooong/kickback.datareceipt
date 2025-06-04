import streamlit as st
import zipfile
import json
import os
from collections import Counter
from datetime import datetime
import tempfile

st.set_page_config(page_title="Kickback (ZIP Upload)", page_icon="🧾")
st.markdown(
    """
    <style>
    /* Import a Google Font (optional) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.title("🧾 Kickback: Upload Your Google Takeout .zip")
st.write("Just drag in your Google Takeout `.zip` file and we’ll generate your data receipt.")

# Processing functions
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

def display_receipt(watch_summary, search_summary):
    st.markdown("---")
    st.subheader("📺 YouTube Watch History")
    st.markdown(f"**Total Videos Watched:** {watch_summary['total_videos']}")
    st.markdown(f"**Estimated Value to Google:** {watch_summary['estimated_value']}")
    st.markdown(f"**Most Active Hour:** {watch_summary['most_active_hour']}")
    st.markdown("**Top Watched Titles:**")
    for title in watch_summary['top_titles']:
        st.markdown(f"- {title}")

    st.subheader("🔍 YouTube Search History")
    st.markdown(f"**Total Searches:** {search_summary['total_searches']}")
    st.markdown(f"**Estimated Value to Google:** {search_summary['estimated_value']}")
    st.markdown("**Top Search Terms:**")
    for term in search_summary['top_searches']:
        st.markdown(f"- {term}")

    st.markdown("---")
    st.subheader("🏷️ Data Label")
    st.markdown("**You are a Terminally Online Curator.**")
    st.markdown("You watched 6,155 videos — enough to fill a film festival that lasts 25 straight days.")
    st.markdown("Your top searches include “channel 5,” “flagrant 2,” and “mac miller type beat.”")
    st.markdown("1,000+ unique searches? You’re not just watching — you’re sifting.")
    st.markdown("You don’t follow the algorithm. The algorithm follows you.")

    total_value = round(
        float(watch_summary['estimated_value'].strip('$')) +
        float(search_summary['estimated_value'].strip('$')),
        2
    )

    st.markdown("---")
    st.subheader("💰 Summary")
    st.markdown(f"**Total Estimated Value Generated for Google:** ${total_value}")
    st.markdown("**You Received:** $0.00 😐")
    st.caption("They watched you watch. Time to take your data back.")

# Upload and process ZIP
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
            st.error("Could not find both `watch-history.json` and `search-history.json` in your .zip file. Make sure you downloaded your data from Google Takeout with YouTube history included.")
