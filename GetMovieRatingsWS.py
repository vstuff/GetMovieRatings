import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Mobile-friendly CSS (same as original)
st.markdown("""
    <style>
    .stDataFrame { width: 100% !important; }
    @media (max-width: 768px) {
        .stColumn { display: block; width: 100%; margin-bottom: 10px; }
        h3 { font-size: 1.2em; }
        h1 { font-size: 1.5em; }
        p { font-size: 0.9em; }
    }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.markdown("<h1 style='text-align: center; color: #1E90FF;'>GetMovieRatingsWS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Ratings and more via Google scraping.</p>", unsafe_allow_html=True)
st.write("*Tip: Enter exact titles (e.g., 'The Matrix')—results may vary.*")

# Form for input
with st.form(key="movie_form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        movie_title = st.text_input("Movie or Show Name", placeholder="e.g., The Matrix")
    with col2:
        language_input = st.text_input("Language (optional)", placeholder="e.g., English, Tamil")
    submit_button = st.form_submit_button(label="Get Ratings & More")

# Scrape Google function
def scrape_google(query):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"}
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Ratings (rough extraction from Knowledge Graph or snippets)
    ratings = {}
    for span in soup.select("span"):
        text = span.text.lower()
        if "imdb" in text and "/10" in text:
            ratings["IMDb"] = span.text.strip()
        elif "rotten tomatoes" in text and "%" in text:
            ratings["Rotten Tomatoes"] = span.text.strip()
    
    # Poster (first image result)
    poster = soup.select_one("img")["src"] if soup.select_one("img") else None
    
    # Wildcard (similar titles from "People also search for")
    wildcard = [a.text for a in soup.select("a") if "people also search for" in a.text.lower() or a.text.strip()]
    
    # Recommendations (related searches)
    recs = [div.text for div in soup.select("div") if "related searches" in div.text.lower() or div.text.strip()]
    
    return ratings, poster, wildcard[:5], recs[:5]

# Process submission
if submit_button and movie_title:
    query = f"{movie_title} ratings {language_input if language_input else ''}"
    ratings, poster_url, wildcard_titles, rec_titles = scrape_google(query)

    if ratings:
        st.success(f"Found results for: {movie_title}")
        
        # Layout for requested movie
        col1, col2 = st.columns([1, 2])
        with col1:
            if poster_url and "http" in poster_url:
                st.image(poster_url, caption=movie_title, use_container_width=True)
            else:
                st.write("No poster found")
        
        with col2:
            st.markdown("### Ratings")
            for source, value in ratings.items():
                if source == "Rotten Tomatoes":
                    st.markdown(f"🍅 <b style='color: #FF4500;'>{source}: {value}</b>", unsafe_allow_html=True)
                elif source == "Internet Movie Database":
                    st.markdown(f"⭐ <b style='color: #FFD700;'>{source}: {value}</b>", unsafe_allow_html=True)
                else:
                    st.markdown(f"📊 <b>{source}: {value}</b>", unsafe_allow_html=True)
            if not ratings:
                st.write("No ratings found")

            # No detailed fields from Google scraping easily available, so skip expander

        # Wildcard table
        st.markdown("<h3 style='text-align: center; margin-top: 20px;'>Top Matches</h3>", unsafe_allow_html=True)
        wildcard_data = []
        for title in wildcard_titles:
            # Rough type guess (not precise without API)
            type_icon = "🎬" if "movie" in title.lower() else "📺" if "series" in title.lower() else "❓"
            wildcard_data.append({
                "Movie Name": title,
                "Year": "N/A",  # Hard to extract reliably
                "Type": type_icon,
                "Genre": "N/A",
                "Language": language_input if language_input else "N/A",
                "Rotten Tomatoes": "N/A",
                "IMDb": "N/A"
            })
        if wildcard_data:
            df_top = pd.DataFrame(wildcard_data)
            st.dataframe(df_top, use_container_width=True)
        else:
            st.write("No similar titles found.")

        # Recommendations table
        st.markdown("<h3 style='text-align: center; margin-top: 20px;'>Recommended For You</h3>", unsafe_allow_html=True)
        rec_data = []
        for title in rec_titles:
            type_icon = "🎬" if "movie" in title.lower() else "📺" if "series" in title.lower() else "❓"
            rec_data.append({
                "Movie Name": title,
                "Year": "N/A",
                "Type": type_icon,
                "Genre": "N/A",
                "Language": language_input if language_input else "N/A",
                "Rotten Tomatoes": "N/A",
                "IMDb": "N/A"
            })
        if rec_data:
            df_recs = pd.DataFrame(rec_data)
            st.dataframe(df_recs, use_container_width=True)
        else:
            st.write("No recommendations found.")
    else:
        st.error("No data found—Google might be blocking or results are incomplete.")
elif submit_button and not movie_title:
    st.warning("Please enter a movie or show name.")