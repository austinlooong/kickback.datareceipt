import streamlit as st
import json
from collections import Counter
from datetime import datetime

st.set_page_config(page_title="Kickback", page_icon="🧾")

st.title("🧾 Kickback: YouTube Data Receipt")
st.write("Upload your Google Takeout `.json` files for YouTube watch and search history to see how much value you created for Google.")

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

# Upload files and load data once
watch_file = st.file_uploader("Upload your watch-history.json", type="json")
search_file = st.file_uploader("Upload your search-history.json", type="json")

if watch_file and search_file:
    watch_data = json.load(watch_file)
    search_data = json.load(search_file)

    watch_summary = generate_watch_summary(watch_data)
    search_summary = parse_youtube_search_history(search_data)

    display_receipt(watch_summary, search_summary)