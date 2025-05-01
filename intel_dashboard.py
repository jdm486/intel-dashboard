import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime, timedelta

# --- Define Clients ---
clients = {
    "Cognito Therapeutics": ["Cognito Therapeutics"],
    "Astria Therapeutics": ["Astria Therapeutics"],
    "Hansa Biopharma": ["Hansa Biopharma"],
    "Tempest Therapeutics": ["Tempest Therapeutics"],
    "Sensius Thermotherapy": ["Sensius Thermotherapy"]
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
        feed_url = get_rss_url(name)
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = entry.title
            summary = entry.get("summary", "")
            published = entry.get("published", "")
            try:
                pub_date = dateti
