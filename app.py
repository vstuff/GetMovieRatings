import streamlit as st
import requests

API_KEY = "92ff2a2e"  # Get this from omdbapi.com
st.title("Movie Ratings Finder")
img_file = st.camera_input("Take a picture of a movie scene")

if img_file is not None:
    st.image(img_file, caption="Captured Image")
    movie_title = "The Matrix"  # Placeholder
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["Response"] == "True":
        st.subheader(data["Title"])
        st.write(f"Year: {data['Year']}")
        st.write(f"Genre: {data['Genre']}")
        st.write(f"Plot: {data['Plot']}")
        st.write(f"IMDb Rating: {data['imdbRating']}")
        ratings = {r["Source"]: r["Value"] for r in data.get("Ratings", [])}
        if "Rotten Tomatoes" in ratings:
            st.write(f"Rotten Tomatoes: {ratings['Rotten Tomatoes']}")
    else:
        st.error("Movie not found!")