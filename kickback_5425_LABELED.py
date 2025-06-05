import streamlit as st
import zipfile
import json
import os
from collections import Counter
from datetime import datetime, time
import tempfile

st.set_page_config(page_title="Kickback (ZIP Upload)", page_icon="🧾")
st.title("🧾 Kickback Data Receipts")
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
    most_common = Counter(watch_hours).most_common(1)
    hour = most_common[0][0] if most_common else 0
    most_active_hour = time(hour).strftime("%-I %p")

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
    unique_terms = len(set(searches))
    return {
        "total_searches": total_searches,
        "unique_terms": unique_terms,
        "estimated_value": f"${estimated_value}",
    }
    
def generate_data_label(watch_summary, search_summary):
    watch_count = watch_summary['total_videos']
    search_count = search_summary['total_searches']
    unique_searches = search_summary['unique_terms']
    most_active_hour = watch_summary['most_active_hour']

    if watch_count > 500 and search_count > 1000:
        return "🧾 Terminally Online Curator", (
            "You don’t consume — you catalog. Your playlists have subtext. "
            "The algorithm tries to catch up, but you're already onto the next niche."
        )
    if unique_searches > 300:
        return "🧠 Thought Spiral Enthusiast", (
            "Your late-night queries include 'how do I know if I’m real' and 'can I marry my best friend.' "
            "You don’t search — you spiral with intention."
        )
    if 3 <= int(most_active.split()[0]) <= 5:
        return "👁️ Panopticon Peeper", (
            "You are the dream user. Consistent. Predictable. Always watching. "
            "Even your boredom has a timestamp."
        )
    if watch_count > 1000 and search_count < 50:
        return "🌀 Algorithm-Generated Human", (
            "You didn’t find YouTube. It found you. "
            "The only thing you searched for was 'lofi beats to dissociate to.'"
        )
    if unique_searches > 200 and search_count > 500:
        return "🛸 Fringe Researcher", (
            "‘Simulation theory’ and ‘hidden ancient tech’ are normal to you. "
            "Google doesn’t judge. It just listens."
        )
    if watch_count < 50 and search_count < 50:
        return "🧃 Low-Impact Lurker", (
            "You leave almost no trace. Maybe that’s on purpose. "
            "Or maybe you just... have a life?"
        )
    if 100 <= watch_count <= 200 and 100 <= search_count <= 200:
        return "👤 Default Human", (
            "You don’t game the algorithm. You *are* the algorithm. "
            "Predictable, pluggable, perfectly marketable."
        )
    if watch_count > 500 and unique_searches < 20:
        return "🔥 Pipeline Candidate", (
            "Your recommendations got darker. Your searches got louder. "
            "You might’ve started with debates — but now you're in the trenches of the algorithm’s war games."
        )
    return "🧾 Terminally Online Curator", (
        "You sift. You organize. You *know*. The algorithm follows you."
)
            
def display_receipt(watch_summary, search_summary):
    st.markdown("---")
    st.subheader("📺 YouTube Watch History")
    st.markdown(f"**Total Videos Watched:** {watch_summary['total_videos']}")
    st.markdown(f"**Estimated Value to Google:** {watch_summary['estimated_value']}")
    st.write("DEBUG watch_summary keys:", watch_summary.keys())
    st.markdown(f"**Most Active Hour:** {watch_summary['most_active_hour']}")
    st.subheader("🔍 YouTube Search History")
    st.markdown(f"**Total Searches:** {search_summary['total_searches']}")
    st.markdown(f"**Estimated Value to Google:** {search_summary['estimated_value']}")
    st.markdown(f"**Total Unique Searches:** {search_summary['unique_terms']}")

    st.markdown("---")
    st.subheader("🏷️ Data Label")
    label, description = generate_data_label(watch_summary, search_summary)
    st.markdown(f"**{label}**")
    st.markdown(description)

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


