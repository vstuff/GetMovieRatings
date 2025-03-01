import streamlit as st
import requests
import pandas as pd

# OMDb API key placeholder
API_KEY = "92ff2a2e"  # Replace with your actual key from omdbapi.com

# Language-aware recommendation dictionary (expandable later)
RECOMMENDATIONS = {
    "Action": {
        "English": ["The Dark Knight", "Mad Max: Fury Road", "Die Hard"],
        "Tamil": ["Baasha", "Thuppakki", "Kaala"]
    },
    "Sci-Fi": {
        "English": ["Blade Runner", "Interstellar", "The Matrix"],
        "Tamil": ["Enthiran", "24", "2.0"]
    },
    "Drama": {
        "English": ["The Shawshank Redemption", "Forrest Gump", "The Godfather"],
        "Tamil": ["Nayakan", "Anbe Sivam", "Roja"]
    },
    "Comedy": {
        "English": ["The Hangover", "Superbad", "Anchorman"],
        "Tamil": ["Michael Madana Kama Rajan", "Panchatanthiram", "Sathi Leelavathi"]
    }
}

# App title and description
st.markdown("<h1 style='text-align: center; color: #1E90FF;'>GetMovieRatings</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Ratings, top matches, and personalized recommendations.</p>", unsafe_allow_html=True)
st.write("*Tip: Use exact titles (e.g., 'The Matrix' or 'Baasha') for best results.*")

# Form for input
with st.form(key="movie_form"):
    movie_title = st.text_input("Movie or Show Name", placeholder="e.g., The Matrix")
    submit_button = st.form_submit_button(label="Get Ratings & More")

# Process submission
if submit_button and movie_title:
    # Exact match fetch
    url = f"http://www.omdbapi.com/?t={movie_title.replace(' ', '+')}&apikey={API_KEY}"
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
            detailed_results = []
            for result in search_results[:10]:  # Fetch details for up to 10 to filter top 5
                detail_url = f"http://www.omdbapi.com/?i={result['imdbID']}&apikey={API_KEY}"
                detail_response = requests.get(detail_url)
                detail_data = detail_response.json()
                if detail_data["Response"] == "True" and detail_data.get("imdbVotes", "0") != "N/A":
                    votes = int(detail_data["imdbVotes"].replace(",", ""))
                    detailed_results.append({
                        "Movie Name": detail_data["Title"],
                        "Genre": detail_data.get("Genre", "N/A"),
                        "Language": detail_data.get("Language", "N/A"),
                        "Rotten Tomatoes": next((r["Value"] for r in detail_data.get("Ratings", []) if r["Source"] == "Rotten Tomatoes"), "N/A"),
                        "IMDb": detail_data.get("imdbRating", "N/A"),
                        "Votes": votes
                    })

            # Sort by IMDb votes and take top 5
            top_5 = sorted(detailed_results, key=lambda x: x["Votes"], reverse=True)[:5]
            if top_5:
                df_top = pd.DataFrame(top_5).drop(columns=["Votes"])  # Drop Votes from display
                st.dataframe(df_top, use_container_width=True)
            else:
                st.write("No similar titles found.")
        else:
            st.write("No similar titles found.")

        # Recommendations table
        st.markdown("<h3 style='text-align: center; margin-top: 20px;'>Recommended For You</h3>", unsafe_allow_html=True)
        genre = data.get("Genre", "").split(", ")[0]
        language = data.get("Language", "English").split(", ")[0]  # Default to English if none
        recs = RECOMMENDATIONS.get(genre, {}).get(language, RECOMMENDATIONS.get(genre, {}).get("English", []))[:3]

        table_data = []
        for rec_title in recs:
            if rec_title != data["Title"]:  # Avoid recommending the input movie
                rec_url = f"http://www.omdbapi.com/?t={rec_title.replace(' ', '+')}&apikey={API_KEY}"
                rec_response = requests.get(rec_url)
                rec_data = rec_response.json()
                if rec_data["Response"] == "True":
                    rec_ratings = rec_data.get("Ratings", [])
                    table_data.append({
                        "Movie Name": rec_data["Title"],
                        "Genre": rec_data.get("Genre", "N/A"),
                        "Language": rec_data.get("Language", "N/A"),
                        "Rotten Tomatoes": next((r["Value"] for r in rec_ratings if r["Source"] == "Rotten Tomatoes"), "N/A"),
                        "IMDb": next((r["Value"] for r in rec_ratings if r["Source"] == "Internet Movie Database"), "N/A")
                    })

        if table_data:
            df_recs = pd.DataFrame(table_data)
            st.dataframe(df_recs, use_container_width=True)
        else:
            st.write("No recommendations available for this genre/language.")

    else:
        st.error("Not found! Check the title and try again.")
elif submit_button and not movie_title:
    st.warning("Please enter a movie or show name.")