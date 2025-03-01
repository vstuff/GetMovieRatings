import streamlit as st
import requests

# Replace with your OMDb API key
API_KEY = "92ff2a2e"  # Should already be set from earlier

# App title
st.title("Movie Ratings Finder")

# Capture image from camera
img_file = st.camera_input("Take a picture of a movie scene")

if img_file is not None:
    # Show the captured image
    st.image(img_file, caption="Captured Image")

    # Let user enter the movie title
    movie_title = st.text_input("Enter the movie title you think this is:")

    # Only fetch data if a title is entered
    if movie_title:
        # Fetch movie data from OMDb API
        url = f"http://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        # Display movie details if found
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
            st.error("Movie not found! Check the title and try again.")