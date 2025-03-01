import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file (API key stored here)
load_dotenv()
API_KEY = os.getenv("OMDB_API_KEY")
if not API_KEY:
    st.error("OMDB_API_KEY not found in environment. Please set it in .env or Streamlit secrets.")
    st.stop()

# CSS for mobile-friendly styling—keeps layout clean and readable
st.markdown("""
    <style>
    body { background-color: #f5f6f5; font-family: 'Arial', sans-serif; }
    h1 { color: #1E90FF; text-align: center; margin-bottom: 0; }
    p { color: #7f8c8d; text-align: center; }
    .stColumn { padding: 10px; }
    .ratings-box { background-color: #ecf0f1; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    a { color: #1E90FF; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .search-links { margin-top: 10px; text-align: center; }
    @media (max-width: 768px) {
        .stColumn { display: block; width: 100%; margin-bottom: 10px; }
        h1 { font-size: 1.5em; }
        p { font-size: 0.9em; }
    }
    </style>
""", unsafe_allow_html=True)

# App title and description—sets the tone for users
st.markdown("<h1>Got Ratings?</h1>", unsafe_allow_html=True)
st.markdown("<p>Ratings at your fingertips—fast and simple.</p>", unsafe_allow_html=True)
st.write("*Tip: Enter exact titles (e.g., 'The Matrix') and optionally a language (e.g., 'Tamil')!*")

# Form for user input—two fields: movie title (required) and language (optional)
with st.form(key="movie_form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        movie_title = st.text_input("Movie or Show Name", placeholder="e.g., The Matrix")
    with col2:
        language = st.text_input("Language (optional)", placeholder="e.g., English, Tamil")
    submit_button = st.form_submit_button(label="Get Ratings & More")

# Process submission when form is submitted
if submit_button and movie_title:
    # Step 1: Exact match search with movie title only—1 API call
    url = f"http://www.omdbapi.com/?t={movie_title.replace(' ', '+')}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    # Check if search succeeded—OMDb returns "Response": "True" on success
    if data["Response"] != "True":
        st.error("Not found! Please use an exact title (e.g., 'Baasha' not 'Basha').")
        st.stop()

    # Step 2: Restrict by language only if exact match exists
    # Default to movie’s language—e.g., “Baasha” → “Tamil”
    searched_language = data.get("Language", "English").split(", ")[0]
    if language and language.lower() != searched_language.lower():
        lang_match = language.lower() == searched_language.lower()
        if not lang_match:
            # Warn if language input doesn’t match movie’s language—proceed anyway
            st.warning(f"'{language}' doesn’t match this movie’s language ({searched_language})—showing results anyway.")
        else:
            searched_language = language  # Use input language if exact match

    # Display matched movie—title as clickable IMDb link
    imdb_id = data.get("imdbID", "")
    imdb_link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else "#"
    st.success("Found:")
    st.markdown(f"<a href='{imdb_link}' target='_blank'>{data['Title']}</a>", unsafe_allow_html=True)

    # Two-column layout: poster on left, ratings/links on right
    col1, col2 = st.columns([1, 2])
    with col1:
        # Show movie poster if available—visual appeal
        poster_url = data.get("Poster", "")
        if poster_url and poster_url != "N/A":
            st.image(poster_url, caption=data['Title'], use_container_width=True)
        else:
            st.write("No poster available")

    with col2:
        # Ratings section—boxed for clarity
        st.markdown("<div class='ratings-box'>", unsafe_allow_html=True)
        st.markdown("### Ratings")
        ratings = data.get("Ratings", [])
        for rating in ratings:
            source = rating["Source"]
            value = rating["Value"]
            if source == "Rotten Tomatoes":
                # RT link—clickable for more info
                rt_link = f"https://www.rottentomatoes.com/search?search={data['Title'].replace(' ', '+')}"
                st.markdown(f"🍅 <b style='color: #FF4500;'><a href='{rt_link}' target='_blank'>{source}: {value}</a></b>", unsafe_allow_html=True)
            elif source == "Internet Movie Database":
                # IMDb link—consistent with title link
                st.markdown(f"⭐ <b style='color: #FFD700;'><a href='{imdb_link}' target='_blank'>{source}: {value}</a></b>", unsafe_allow_html=True)
            else:
                st.markdown(f"📊 <b>{source}: {value}</b>", unsafe_allow_html=True)
        if not ratings:
            st.write("No ratings available")
        
        # Search links—external options for users (no API calls)
        google_search_url = f"https://www.google.com/search?q={movie_title.replace(' ', '+')}+movie+ratings"
        imdb_search_url = f"https://www.imdb.com/find?q={movie_title.replace(' ', '+')}&s=tt"
        letterboxd_search_url = f"https://letterboxd.com/search/{movie_title.replace(' ', '+')}/"
        st.markdown(
            f"<div class='search-links'>"
            f"<a href='{google_search_url}' target='_blank'>Google Search</a> | "
            f"<a href='{imdb_search_url}' target='_blank'>IMDb Search</a> | "
            f"<a href='{letterboxd_search_url}' target='_blank'>Letterboxd Search</a>"
            f"</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Expandable details—extra info on demand
        with st.expander("Details"):
            for key, value in data.items():
                if key not in ["Response", "Ratings", "Poster"] and value and value != "N/A":
                    st.write(f"**{key}**: {value}")

else:
    # Warn if no title entered—form validation
    if submit_button and not movie_title:
        st.warning("Please enter a movie or show name.")