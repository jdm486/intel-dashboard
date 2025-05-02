import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime, timedelta

# --- Define Clients and Competitors ---
clients = {
    "Cognito Therapeutics": ["Cognito Therapeutics"],
    "Astria Therapeutics": ["Astria Therapeutics"],
    "Hansa Biopharma": ["Hansa Biopharma"],
    "Tempest Therapeutics": ["Tempest Therapeutics"],
    "Sensius Thermotherapy": ["Sensius Thermotherapy"]
}

competitors = {
    "Cognito Therapeutics": ["Sinaptica Therapeutics", "NeuroEM Therapeutics", "Functional Neuromodulation", "OptoCeutics"],
    "Astria Therapeutics": ["Takeda", "BioCryst", "KalVista Pharmaceuticals", "Pharvaris", "Sanofi", "Roche", "Amgen"],
    "Hansa Biopharma": ["Alexion", "CSL Behring", "Sobi", "Natera"],
    "Tempest Therapeutics": ["Arcus Biosciences", "Incyte", "Surface Oncology", "Akeso Biopharma"],
    "Sensius Thermotherapy": ["Pyrexar Medical", "OncoTherm", "BSD Medical", "ThermMed"]
}

# --- Keywords for Categorization ---
categories = {
    "Funding": ["funding", "series", "investment", "raises", "round"],
    "Clinical Trial": ["clinical", "trial", "phase", "enrollment"],
    "Data/Publication": ["data", "publication", "study", "results", "efficacy"],
    "People Moves": [
        "appoints", "ceo", "cfo", "coo", "chief", "CMO", "CSO", "VP", "joins", "new hire", "head of",
        "resignation", "resigns", "leaving", "layoffs", "redundancies", "let go", "restructure", "staff cuts", "job cuts"
    ],
    "Job Postings": ["hiring", "job opening", "now hiring", "career opportunity", "apply now", "recruiting"],
    "Partnership/Acquisition": ["partner", "acquire", "acquisition", "merger", "collaborate", "license", "research partner"],
    "Regulatory Update": ["FDA", "EMA", "approval", "designation", "breakthrough", "IND", "NDA"],
    "Commercial Move": ["launch", "commercial", "pricing", "reimbursement", "market access"],
    "Investor Relations": ["earnings", "quarterly", "shareholder", "investor", "guidance"],
    "Pipeline Milestone": ["milestone", "readout", "development", "update"],
    "Upcoming Event": ["conference", "presenting at", "presentation", "poster", "abstract", "upcoming", "speaking at", "webinar"],
    "Setback/Risk": ["pause", "terminated", "hold", "FDA rejection", "negative"]
}

# --- Strategic Groupings ---
rd_cats = ["Clinical Trial", "Data/Publication", "Pipeline Milestone"]
corp_cats = ["Funding", "People Moves", "Job Postings", "Partnership/Acquisition", "Investor Relations"]
risk_cats = ["Regulatory Update", "Setback/Risk", "Commercial Move"]
event_cats = ["Upcoming Event"]

# --- Utility Functions ---
def get_rss_url(query):
    return f"https://news.google.com/rss/search?q={query.replace(' ', '+')}"

def categorize(text):
    tags = []
    lower_text = text.lower()
    for cat, keys in categories.items():
        if any(k.lower() in lower_text for k in keys):
            tags.append(cat)
    return ", ".join(tags) if tags else "Other"

def fetch_news(names):
    entries = []
    for name in names:
        try:
            feed_url = get_rss_url(name)
            feed = feedparser.parse(feed_url)
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
        except Exception as e:
            st.warning(f"Failed to fetch news for {name}: {e}")
            continue
    return entries

# --- Streamlit UI ---
st.set_page_config(page_title="Real time news for Joseph's Company Watch List", layout="wide")
st.title("📡 Real time news for Joseph's Company Watch List")

# --- Sidebar Filters ---
st.sidebar.header("Filters")
client_selection = st.sidebar.selectbox("Select client to view", list(clients.keys()) + ["All"])
search_query = st.sidebar.text_input("Search keyword")
time_filter = st.sidebar.selectbox("Show updates from:", ["Last 24 hours", "Last 7 days", "Last 30 days", "All time"])

# --- Fetch News ---
st.info("Fetching latest news... This may take a few seconds.")
if client_selection == "All":
    all_names = [name for names in clients.values() for name in names]
    competitor_names = [c for group in competitors.values() for c in group]
else:
    all_names = clients[client_selection]
    competitor_names = competitors.get(client_selection, [])

client_news = fetch_news(all_names)
competitor_news = fetch_news(competitor_names)

# --- Create DataFrames ---

def filter_dataframe(df):
    df = df.copy()
    df.dropna(subset=["Published"], inplace=True)
    if time_filter == "Last 24 hours":
        df = df[df["Published"] >= datetime.now() - timedelta(days=1)]
    elif time_filter == "Last 7 days":
        df = df[df["Published"] >= datetime.now() - timedelta(days=7)]
    elif time_filter == "Last 30 days":
        df = df[df["Published"] >= datetime.now() - timedelta(days=30)]
    if search_query:
        df = df[df["Title"].str.contains(search_query, case=False, na=False) |
                df["Company"].str.contains(search_query, case=False, na=False)]
    return df

df_clients = filter_dataframe(pd.DataFrame(client_news))
df_competitors = filter_dataframe(pd.DataFrame(competitor_news))

for df in [df_clients, df_competitors]:
    df.dropna(subset=["Published"], inplace=True)
    if time_filter == "Last 24 hours":
        df = df[df["Published"] >= datetime.now() - timedelta(days=1)]
    elif time_filter == "Last 7 days":
        df = df[df["Published"] >= datetime.now() - timedelta(days=7)]
    elif time_filter == "Last 30 days":
        df = df[df["Published"] >= datetime.now() - timedelta(days=30)]
    if search_query:
        df = df[df["Title"].str.contains(search_query, case=False, na=False) |
                df["Company"].str.contains(search_query, case=False, na=False)]

if df_clients.empty and df_competitors.empty:
    st.warning("No news articles found. Try changing your filters or timeframe.")
    st.stop()

# --- Layout: Client News ---
st.markdown("## 🧬 Company R&D and Data")
col1, col2 = st.columns(2)
for category in rd_cats:
    with col1 if rd_cats.index(category) % 2 == 0 else col2:
        subset = df_clients[df_clients["Category"].str.contains(category)]
        if not subset.empty:
            st.markdown(f"#### 🔍 <small>{category}</small>", unsafe_allow_html=True)
            for _, row in subset.iterrows():
                st.markdown(f"**{row['Title']}**  ")
                st.markdown(f"{row['Company']} | Published: {row['Published'].strftime('%Y-%m-%d')}  ")
                st.markdown(f"[Read more]({row['Link']})")
                st.markdown("---")

st.markdown("## 🚨 Company Risk and Regulatory")
col5, col6 = st.columns(2)
for category in risk_cats:
    with col5 if risk_cats.index(category) % 2 == 0 else col6:
        subset = df_clients[df_clients["Category"].str.contains(category)]
        if not subset.empty:
            st.markdown(f"### ⚠️ <small>{category}</small>", unsafe_allow_html=True)
            for _, row in subset.iterrows():
                st.markdown(f"**{row['Title']}**  ")
                st.markdown(f"{row['Company']} | Published: {row['Published'].strftime('%Y-%m-%d')}  ")
                st.markdown(f"[Read more]({row['Link']})")
                st.markdown("---")

st.markdown("## 📅 Company Upcoming Events and Presentations")
subset = df_clients[df_clients["Category"].str.contains("Upcoming Event")]
if not subset.empty:
    for _, row in subset.iterrows():
        st.markdown(f"**{row['Title']}**  ")
        st.markdown(f"{row['Company']} | Published: {row['Published'].strftime('%Y-%m-%d')}  ")
        st.markdown(f"[Read more]({row['Link']})")
        st.markdown("---")

# --- Layout: Competitor News ---
st.markdown("## 🧪 Relevant Competitor Information")
col7, col8 = st.columns(2)
for category in rd_cats + corp_cats + risk_cats + event_cats:
    with col7 if (rd_cats + corp_cats + risk_cats + event_cats).index(category) % 2 == 0 else col8:
        subset = df_competitors[df_competitors["Category"].str.contains(category)]
        if not subset.empty:
            st.markdown(f"#### 📎 <small>{category} (Competitor)</small>", unsafe_allow_html=True)
            for _, row in subset.iterrows():
                st.markdown(f"**{row['Title']}**  ")
                st.markdown(f"{row['Company']} | Published: {row['Published'].strftime('%Y-%m-%d')}  ")
                st.markdown(f"[Read more]({row['Link']})")
                st.markdown("---")
