import streamlit as st
import requests
import pandas as pd

# OMDb API key placeholder
API_KEY = "92ff2a2e"  # Replace with your actual key from omdbapi.com

# Language- and type-aware recommendation dictionary
RECOMMENDATIONS = {
    "Action": {
        "English": {
            "movie": ["The Dark Knight", "Mad Max: Fury Road", "Die Hard"],
            "series": ["Breaking Bad", "24", "The Boys"]
        },
        "Tamil": {
            "movie": ["Baasha", "Thuppakki", "Sivaji: The Boss"],
            "series": ["Navarasa", "Asuravithu", "Aaranya Kaandam"]  # Limited series data, placeholders
        }
    },
    "Sci-Fi": {
        "English": {
            "movie": ["Blade Runner", "Interstellar", "The Matrix"],
            "series": ["Stranger Things", "Westworld", "Black Mirror"]
        },
        "Tamil": {
            "movie": ["Enthiran", "24", "2.0"],
            "series": ["Time Enna Boss", "Triples", "Karthik Dial Seytha Yenn"]  # Sparse, placeholders
        }
    },
    "Drama": {
        "English": {
            "movie": ["The Shawshank Redemption", "Forrest Gump", "The Godfather"],
            "series": ["The Sopranos", "The Wire", "Mad Men"]
        },
        "Tamil": {
            "movie": ["Nayakan", "Anbe Sivam", "Pariyerum Perumal"],
            "series": ["Queen", "Suzhal - The Vortex", "Mandala Murders"]
        }
    },
    "Comedy": {
        "English": {
            "movie": ["The Hangover", "Superbad", "Anchorman"],
            "series": ["The Office", "Brooklyn Nine-Nine", "Parks and Recreation"]
        },
        "Tamil": {
            "movie": ["Michael Madana Kama Rajan", "Panchatanthiram", "Sathi Leelavathi"],
            "series": ["Time Enna Boss", "Lollu Sabha", "Triples"]
        }
    }
}

# Mobile-friendly CSS
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
st.markdown("<h1 style='text-align: center; color: #1E90FF;'>GetMovieRatings</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Ratings, top matches, and recommendations.</p>", unsafe_allow_html=True)
st.write("*Tip: Use exact titles (e.g., 'The Matrix' or 'Baasha')—language optional.*")

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
    # Exact match fetch
    url_params = f"t={movie_title.replace(' ', '+')}"
    if language_input:
        url_params += f"&language={language_input.lower()}"
    url = f"http://www.omdbapi.com/?{url_params}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["Response"] == "True":
        st.success(f"Found: {data['Title']}")

        # Two-column layout for requested movie
        col1, col2 = st.columns([1, 2])
        with col1:
            poster_url = data.get("Poster", "")
            if poster_url and poster_url != "N/A":
                st.image(poster_url, caption=data['Title'], use_container_width=True)
            else:
                st.write("No poster available")

        with col2:
            st.markdown("### Ratings")
            ratings = data.get("Ratings", [])
            for rating in ratings:
                source = rating["Source"]
                value = rating["Value"]
                if source == "Rotten Tomatoes":
                    st.markdown(f"🍅 <b style='color: #FF4500;'>{source}: {value}</b>", unsafe_allow_html=True)
                elif source == "Internet Movie Database":
                    st.markdown(f"⭐ <b style='color: #FFD700;'>{source}: {value}</b>", unsafe_allow_html=True)
                else:
                    st.markdown(f"📊 <b>{source}: {value}</b>", unsafe_allow_html=True)
            if not ratings:
                st.write("No ratings available")

            with st.expander("Details"):
                for key, value in data.items():
                    if key not in ["Response", "Ratings", "Poster"] and value and value != "N/A":
                        st.write(f"**{key}**: {value}")

        # Wildcard search for top 5 similar names
        st.markdown("<h3 style='text-align: center; margin-top: 20px;'>Top Rated Movies with Similar Names</h3>", unsafe_allow_html=True)
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
                        detailed_results[title] = {
                            "Movie Name": title,
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
                df_top = pd.DataFrame(top_5).drop(columns=["Votes"])
                st.dataframe(df_top, use_container_width=True)
            else:
                st.write("No similar titles found.")
        else:
            st.write("No similar titles found.")

        # Recommendations table with language and type precedence
        st.markdown("<h3 style='text-align: center; margin-top: 20px;'>Recommended For You</h3>", unsafe_allow_html=True)
        genre = data.get("Genre", "").split(", ")[0]
        searched_language = language_input if language_input else data.get("Language", "English").split(", ")[0]
        searched_type = data.get("Type", "movie")  # Default to movie if not specified
        recs = RECOMMENDATIONS.get(genre, {}).get(searched_language, {}).get(searched_type, [])

        # If no type-specific recs, fallback to any in that language, then English
        if not recs:
            for t in ["movie", "series"]:
                recs = RECOMMENDATIONS.get(genre, {}).get(searched_language, {}).get(t, [])
                if recs:
                    break
        if not recs:
            recs = RECOMMENDATIONS.get(genre, {}).get("English", {}).get(searched_type, [])[:5]

        table_data = {}
        for rec_title in recs[:5]:
            if rec_title != data["Title"]:
                rec_url = f"http://www.omdbapi.com/?t={rec_title.replace(' ', '+')}&apikey={API_KEY}"
                rec_response = requests.get(rec_url)
                rec_data = rec_response.json()
                if rec_data["Response"] == "True":
                    title = rec_data["Title"]
                    if title not in table_data:
                        rec_ratings = rec_data.get("Ratings", [])
                        table_data[title] = {
                            "Movie Name": title,
                            "Year": rec_data.get("Year", "N/A"),
                            "Type": "🎬" if rec_data["Type"] == "movie" else "📺" if rec_data["Type"] == "series" else "❓",
                            "Genre": rec_data.get("Genre", "N/A"),
                            "Language": rec_data.get("Language", "N/A"),
                            "Rotten Tomatoes": next((r["Value"] for r in rec_ratings if r["Source"] == "Rotten Tomatoes"), "N/A"),
                            "IMDb": next((r["Value"] for r in rec_ratings if r["Source"] == "Internet Movie Database"), "N/A")
                        }

        if table_data:
            df_recs = pd.DataFrame(list(table_data.values()))
            st.dataframe(df_recs, use_container_width=True)
        else:
            st.write("No recommendations available for this genre/language/type.")

    else:
        st.error("Not found! Check the title and try again.")
elif submit_button and not movie_title:
    st.warning("Please enter a movie or show name.")