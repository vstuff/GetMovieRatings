import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("OMDB_API_KEY")
if not API_KEY:
    st.error("OMDB_API_KEY not found in environment. Please set it in .env or Streamlit secrets.")
    st.stop()

# Limited static dictionary as seeds (not exhaustive)
SEED_TITLES = {
    "Action": {
        "English": {
            "movie": ["The Dark Knight", "Mad Max: Fury Road", "John Wick"],
            "series": ["Breaking Bad", "24", "The Boys"]
        },
        "Tamil": {
            "movie": ["Baasha", "Thuppakki", "Sivaji: The Boss"],
            "series": ["Navarasa", "Auto Shankar", "Kallachirippu"]
        }
    },
    "Sci-Fi": {
        "English": {
            "movie": ["Interstellar", "The Matrix", "Blade Runner"],
            "series": ["Stranger Things", "Westworld", "Black Mirror"]
        },
        "Tamil": {
            "movie": ["Enthiran", "24", "2.0"],
            "series": ["Time Enna Boss", "Triples", "Karthik Dial Seytha Yenn"]
        }
    },
    "Drama": {
        "English": {
            "movie": ["The Shawshank Redemption", "Forrest Gump", "The Godfather"],
            "series": ["The Sopranos", "The Wire", "Mad Men"]
        },
        "Tamil": {
            "movie": ["Nayakan", "Anbe Sivam", "Pariyerum Perumal"],
            "series": ["Queen", "Suzhal - The Vortex", "Family Man"]
        }
    },
    "Comedy": {
        "English": {
            "movie": ["The Hangover", "Superbad", "Anchorman"],
            "series": ["The Office", "Brooklyn Nine-Nine", "Friends"]
        },
        "Tamil": {
            "movie": ["Michael Madana Kama Rajan", "Panchatanthiram", "Sathi Leelavathi"],
            "series": ["Time Enna Boss", "Lollu Sabha", "Triples"]
        }
    }
}

# Enhanced mobile-friendly CSS with colors and table styling
st.markdown("""
    <style>
    body { background-color: #f5f6f5; font-family: 'Arial', sans-serif; }
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    .custom-table th, .custom-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    .custom-table th { background-color: #ecf0f1; color: #2c3e50; }
    .custom-table tr:nth-child(even) { background-color: #f9f9f9; }
    h1 { color: #1E90FF; text-align: center; margin-bottom: 0; }
    h3 { color: #2c3e50; text-align: center; margin-top: 20px; }
    p { color: #7f8c8d; text-align: center; }
    .stColumn { padding: 10px; }
    .ratings-box { background-color: #ecf0f1; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .section-box { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-top: 20px; }
    a { color: #1E90FF; text-decoration: none; }
    a:hover { text-decoration: underline; }
    @media (max-width: 768px) {
        .stColumn { display: block; width: 100%; margin-bottom: 10px; }
        h3 { font-size: 1.2em; }
        h1 { font-size: 1.5em; }
        p { font-size: 0.9em; }
        .custom-table th, .custom-table td { font-size: 0.9em; padding: 6px; }
    }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.markdown("<h1>GetMovieRatings</h1>", unsafe_allow_html=True)
st.markdown("<p>Ratings, top matches, and personalized recommendations.</p>", unsafe_allow_html=True)
st.write("*Tip: Use exact titles (e.g., 'The Matrix' or 'Baasha')—misspellings are forgiven!*")

# Form for input
with st.form(key="movie_form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        movie_title = st.text_input("Movie or Show Name", placeholder="e.g., The Matrix")
    with col2:
        language_input = st.text_input("Language (optional)", placeholder="e.g., English, Tamil")
    submit_button = st.form_submit_button(label="Get Ratings & More")

# Process submission
if submit_button and movie_title:
    # Try exact match first
    url_params = f"t={movie_title.replace(' ', '+')}"
    if language_input:
        url_params += f"&language={language_input.lower()}"
    url = f"http://www.omdbapi.com/?{url_params}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    # If exact match fails, fall back to wildcard search
    if data["Response"] != "True":
        search_url = f"http://www.omdbapi.com/?s={movie_title.replace(' ', '+')}&apikey={API_KEY}"
        search_response = requests.get(search_url)
        search_data = search_response.json()
        
        if search_data.get("Response") == "True" and "Search" in search_data:
            best_match = None
            max_votes = -1
            for result in search_data["Search"][:5]:
                detail_url = f"http://www.omdbapi.com/?i={result['imdbID']}&apikey={API_KEY}"
                detail_response = requests.get(detail_url)
                detail_data = detail_response.json()
                if detail_data["Response"] == "True" and detail_data.get("imdbVotes", "0") != "N/A":
                    votes = int(detail_data["imdbVotes"].replace(",", ""))
                    if votes > max_votes:
                        max_votes = votes
                        best_match = detail_data
            if best_match:
                data = best_match
                st.info(f"Did you mean '{data['Title']}'? Showing results for the closest match.")
            else:
                st.error("No close matches found. Try a different spelling.")
                st.stop()
        else:
            st.error("Not found! Check the title and try again.")
            st.stop()

    # Proceed with matched data
    imdb_id = data.get("imdbID", "")
    imdb_link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else "#"
    st.success("Found:")
    st.markdown(f"<a href='{imdb_link}' target='_blank'>{data['Title']}</a>", unsafe_allow_html=True)

    # Two-column layout for requested movie
    col1, col2 = st.columns([1, 2])
    with col1:
        poster_url = data.get("Poster", "")
        if poster_url and poster_url != "N/A":
            st.image(poster_url, caption=data['Title'], use_container_width=True)
        else:
            st.write("No poster available")

    with col2:
        st.markdown("<div class='ratings-box'>", unsafe_allow_html=True)
        st.markdown("### Ratings")
        ratings = data.get("Ratings", [])
        for rating in ratings:
            source = rating["Source"]
            value = rating["Value"]
            if source == "Rotten Tomatoes":
                rt_link = f"https://www.rottentomatoes.com/search?search={data['Title'].replace(' ', '+')}"
                st.markdown(f"🍅 <b style='color: #FF4500;'><a href='{rt_link}' target='_blank'>{source}: {value}</a></b>", unsafe_allow_html=True)
            elif source == "Internet Movie Database":
                st.markdown(f"⭐ <b style='color: #FFD700;'><a href='{imdb_link}' target='_blank'>{source}: {value}</a></b>", unsafe_allow_html=True)
            else:
                st.markdown(f"📊 <b>{source}: {value}</b>", unsafe_allow_html=True)
        if not ratings:
            st.write("No ratings available")
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Details"):
            for key, value in data.items():
                if key not in ["Response", "Ratings", "Poster"] and value and value != "N/A":
                    st.write(f"**{key}**: {value}")

    # Wildcard search
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.markdown("<h3>Top Rated Movies with Similar Names</h3>", unsafe_allow_html=True)
    search_url = f"http://www.omdbapi.com/?s={movie_title.replace(' ', '+')}&apikey={API_KEY}"
    search_response = requests.get(search_url)
    search_data = search_response.json()

    if search_data.get("Response") == "True" and "Search" in search_data:
        search_results = search_data["Search"]
        detailed_results = {}
        for result in search_results[:10]:
            detail_url = f"http://www.omdbapi.com/?i={result['imdbID']}&apikey={API_KEY}"
            detail_response = requests.get(detail_url)
            detail_data = detail_response.json()
            if detail_data["Response"] == "True" and detail_data.get("imdbVotes", "0") != "N/A":
                title = detail_data["Title"]
                if title not in detailed_results:
                    votes = int(detail_data["imdbVotes"].replace(",", ""))
                    imdb_id = detail_data.get("imdbID", "")
                    link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else "#"
                    detailed_results[title] = {
                        "Movie Name": f"<a href='{link}' target='_blank'>{title}</a>",
                        "Year": detail_data.get("Year", "N/A"),
                        "Type": "🎬" if detail_data["Type"] == "movie" else "📺" if detail_data["Type"] == "series" else "❓",
                        "Genre": detail_data.get("Genre", "N/A"),
                        "Language": detail_data.get("Language", "N/A"),
                        "Rotten Tomatoes": next((r["Value"] for r in detail_data.get("Ratings", []) if r["Source"] == "Rotten Tomatoes"), "N/A"),
                        "IMDb": detail_data.get("imdbRating", "N/A"),
                        "Votes": votes
                    }

        top_5 = sorted(detailed_results.values(), key=lambda x: x["Votes"], reverse=True)[:5]
        if top_5:
            table_html = "<table class='custom-table'><tr><th>Movie Name</th><th>Year</th><th>Type</th><th>Genre</th><th>Language</th><th>Rotten Tomatoes</th><th>IMDb</th></tr>"
            for row in top_5:
                table_html += f"<tr><td>{row['Movie Name']}</td><td>{row['Year']}</td><td>{row['Type']}</td><td>{row['Genre']}</td><td>{row['Language']}</td><td>{row['Rotten Tomatoes']}</td><td>{row['IMDb']}</td></tr>"
            table_html += "</table>"
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.write("No similar titles found.")
    else:
        st.write("No similar titles found.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Hybrid recommendations: Seed dict + dynamic expansion
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.markdown("<h3>Recommended For You</h3>", unsafe_allow_html=True)
    genre = data.get("Genre", "").split(", ")[0]
    searched_language = language_input if language_input else data.get("Language", "English").split(", ")[0]
    searched_type = data.get("Type", "movie")

    # Stage 1: Start with seed titles
    table_data = {}
    seeds = SEED_TITLES.get(genre, {}).get(searched_language, {}).get(searched_type, [])
    for seed in seeds:
        if len(table_data) >= 5:
            break
        rec_url = f"http://www.omdbapi.com/?t={seed.replace(' ', '+')}&apikey={API_KEY}"
        rec_response = requests.get(rec_url)
        rec_data = rec_response.json()
        if rec_data["Response"] == "True":
            title = rec_data["Title"]
            if title != data["Title"] and title not in table_data:
                votes = int(rec_data.get("imdbVotes", "0").replace(",", ""))
                imdb_id = rec_data.get("imdbID", "")
                link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else "#"
                rec_ratings = rec_data.get("Ratings", [])
                table_data[title] = {
                    "Movie Name": f"<a href='{link}' target='_blank'>{title}</a>",
                    "Year": rec_data.get("Year", "N/A"),
                    "Type": "🎬" if rec_data["Type"] == "movie" else "📺" if rec_data["Type"] == "series" else "❓",
                    "Genre": rec_data.get("Genre", "N/A"),
                    "Language": rec_data.get("Language", "N/A"),
                    "Rotten Tomatoes": next((r["Value"] for r in rec_ratings if r["Source"] == "Rotten Tomatoes"), "N/A"),
                    "IMDb": rec_data.get("imdbRating", "N/A"),
                    "Votes": votes
                }

    # Stage 2: Expand dynamically using a seed title
    if len(table_data) < 5 and seeds:
        seed_title = seeds[0]  # Use first seed as pivot
        rec_url = f"http://www.omdbapi.com/?s={seed_title.replace(' ', '+')}&type={searched_type}&apikey={API_KEY}"
        rec_response = requests.get(rec_url)
        rec_data = rec_response.json()
        if rec_data.get("Response") == "True" and "Search" in rec_data:
            for result in rec_data["Search"][:20]:
                detail_url = f"http://www.omdbapi.com/?i={result['imdbID']}&apikey={API_KEY}"
                detail_response = requests.get(detail_url)
                detail_data = detail_response.json()
                if detail_data["Response"] == "True" and detail_data.get("imdbVotes", "0") != "N/A":
                    title = detail_data["Title"]
                    if title != data["Title"] and title not in table_data:
                        lang_match = searched_language.lower() == detail_data.get("Language", "").lower().split(", ")[0]
                        type_match = detail_data["Type"] == searched_type
                        genre_match = genre.lower() in detail_data.get("Genre", "").lower()
                        if lang_match and type_match and genre_match:
                            votes = int(detail_data["imdbVotes"].replace(",", ""))
                            imdb_id = detail_data.get("imdbID", "")
                            link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else "#"
                            rec_ratings = detail_data.get("Ratings", [])
                            table_data[title] = {
                                "Movie Name": f"<a href='{link}' target='_blank'>{title}</a>",
                                "Year": detail_data.get("Year", "N/A"),
                                "Type": "🎬" if detail_data["Type"] == "movie" else "📺" if detail_data["Type"] == "series" else "❓",
                                "Genre": detail_data.get("Genre", "N/A"),
                                "Language": detail_data.get("Language", "N/A"),
                                "Rotten Tomatoes": next((r["Value"] for r in rec_ratings if r["Source"] == "Rotten Tomatoes"), "N/A"),
                                "IMDb": detail_data.get("imdbRating", "N/A"),
                                "Votes": votes
                            }
                        if len(table_data) >= 5:
                            break

    # Pass 3: Same language, any type, same genre (if needed)
    if len(table_data) < 5:
        alt_type = "series" if searched_type == "movie" else "movie"
        if seeds:
            seed_title = seeds[0]
            rec_url = f"http://www.omdbapi.com/?s={seed_title.replace(' ', '+')}&type={alt_type}&apikey={API_KEY}"
            rec_response = requests.get(rec_url)
            rec_data = rec_response.json()
            if rec_data.get("Response") == "True" and "Search" in rec_data:
                for result in rec_data["Search"][:20]:
                    detail_url = f"http://www.omdbapi.com/?i={result['imdbID']}&apikey={API_KEY}"
                    detail_response = requests.get(detail_url)
                    detail_data = detail_response.json()
                    if detail_data["Response"] == "True" and detail_data.get("imdbVotes", "0") != "N/A":
                        title = detail_data["Title"]
                        if title != data["Title"] and title not in table_data:
                            lang_match = searched_language.lower() == detail_data.get("Language", "").lower().split(", ")[0]
                            genre_match = genre.lower() in detail_data.get("Genre", "").lower()
                            if lang_match and genre_match:
                                votes = int(detail_data["imdbVotes"].replace(",", ""))
                                imdb_id = detail_data.get("imdbID", "")
                                link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else "#"
                                rec_ratings = detail_data.get("Ratings", [])
                                table_data[title] = {
                                    "Movie Name": f"<a href='{link}' target='_blank'>{title}</a>",
                                    "Year": detail_data.get("Year", "N/A"),
                                    "Type": "🎬" if detail_data["Type"] == "movie" else "📺" if detail_data["Type"] == "series" else "❓",
                                    "Genre": detail_data.get("Genre", "N/A"),
                                    "Language": detail_data.get("Language", "N/A"),
                                    "Rotten Tomatoes": next((r["Value"] for r in rec_ratings if r["Source"] == "Rotten Tomatoes"), "N/A"),
                                    "IMDb": detail_data.get("imdbRating", "N/A"),
                                    "Votes": votes
                                }
                            if len(table_data) >= 5:
                                break

    # Sort and limit to 5
    if table_data:
        top_recs = sorted(table_data.values(), key=lambda x: x["Votes"], reverse=True)[:5]
        table_html = "<table class='custom-table'><tr><th>Movie Name</th><th>Year</th><th>Type</th><th>Genre</th><th>Language</th><th>Rotten Tomatoes</th><th>IMDb</th></tr>"
        for row in top_recs:
            table_html += f"<tr><td>{row['Movie Name']}</td><td>{row['Year']}</td><td>{row['Type']}</td><td>{row['Genre']}</td><td>{row['Language']}</td><td>{row['Rotten Tomatoes']}</td><td>{row['IMDb']}</td></tr>"
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.write(f"No recommendations found in {searched_language} for {genre} {searched_type}s—OMDb may lack matching titles.")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    if submit_button and not movie_title:
        st.warning("Please enter a movie or show name.")