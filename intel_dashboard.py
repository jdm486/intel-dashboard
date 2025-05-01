import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime, timedelta

# --- Define Clients and Competitors ---
companies = {
    "Cognito Therapeutics": ["Cognito Therapeutics", "NeuroEM", "E-Scape Bio", "Alzheon"],
    "Astria Therapeutics": ["Astria Therapeutics", "Pharvaris", "BioCryst", "Takeda", "KalVista"],
    "Hansa Biopharma": ["Hansa Biopharma", "Alexion", "Sobi", "CSL Behring"],
    "Sensius Thermotherapy": ["Sensius Thermotherapy", "Pyrexar", "BSD Medical", "Oncotherm"],
    "Tempest": ["Tempest", "Pear Therapeutics", "Akili Interactive", "BetterHelp", "Talkspace"]
}

# --- Keywords for Categorization ---
categories = {
    "Funding": ["funding", "series", "investment", "raises", "round"],
    "Clinical Trial": ["clinical", "trial", "phase", "enrollment"],
    "Data/Publication": ["data", "publication", "study", "results", "efficacy"],
    "Leadership Change": ["appoints", "ceo", "cfo", "coo", "chief"],
    "Partnership/Acquisition": ["partner", "acquire", "acquisition", "merger"]
}

# --- Utility Functions ---
def get_rss_url(query):
    return f"https://news.google.com/rss/search?q={query.replace(' ', '+')}"

def categorize(text):
    tags = []
    lower_text = text.lower()
    for cat, keys in categories.items():
        if any(k in lower_text for k in keys):
            tags.append(cat)
    return ", ".join(tags) if tags else "Other"

def fetch_news(name):
    feed_url = get_rss_url(name)
    feed = feedparser.parse(feed_url)
    entries = []
    for entry in feed.entries:
        title = entry.title
        summary = entry.get("summary", "")
        published = entry.get("published", "")
        try:
            pub_date = datetime.strptime(published[:16], "%a, %d %b %Y")
        except:
            pub_date = None
        text = f"{title} {summary}"
        entries.append({
            "Company": name,
            "Title": title,
            "Link": entry.link,
            "Published": pub_date,
            "Category": categorize(text)
        })
    return entries

# --- Streamlit UI ---
st.set_page_config(page_title="Biotech Intel Dashboard", layout="wide")
st.title("🧠 Client & Competitor Intelligence Dashboard")

# --- Sidebar Filters ---
st.sidebar.header("Filters")
search_query = st.sidebar.text_input("Search company or keyword")
recent_only = st.sidebar.checkbox("Show only last 7 days", value=True)

# --- Fetch News ---
st.info("Fetching latest news... This may take a few seconds.")
all_entries = []
for group in companies.values():
    for name in group:
        all_entries.extend(fetch_news(name))

# --- Create DataFrame ---
df = pd.DataFrame(all_entries)
df.dropna(subset=["Published"], inplace=True)
if recent_only:
    df = df[df["Published"] >= datetime.now() - timedelta(days=7)]
if search_query:
    df = df[df["Title"].str.contains(search_query, case=False, na=False) |
            df["Company"].str.contains(search_query, case=False, na=False)]

# --- Display ---
df.sort_values("Published", ascending=False, inplace=True)
for _, row in df.iterrows():
    st.markdown(f"**{row['Title']}**  ")
    st.markdown(f"{row['Company']} — {row['Category']}  ")
    st.markdown(f"Published: {row['Published'].strftime('%Y-%m-%d')}  ")
    st.markdown(f"[Read more]({row['Link']})")
    st.markdown("---")
