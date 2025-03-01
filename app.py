import streamlit as st
import requests

# Replace with your OMDb API key
API_KEY = "92ff2a2e"  # e.g., "1234abcd" from omdbapi.com

# App title and description
st.title("Movie & Show Ratings Finder")
st.write("Enter a movie or show name for which you want to find the rating")

# Text input for movie/show name
movie_title = st.text_input("Movie or Show Name", placeholder="e.g., The Matrix")

# Submit button
if st.button("Get Rating"):
    if movie_title:
        # Fetch data from OMDb API
        url = f"http://www.omdbapi.com/?t={movie_title.replace(' ', '+')}&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        # Check if data was found
        if data["Response"] == "True":
            st.success(f"Found: {data['Title']}")
            # Display all fields dynamically
            for key, value in data.items():
                if key != "Response" and value and value != "N/A":  # Skip empty or irrelevant fields
                    st.write(f"**{key}**: {value}")
        else:
            st.error("Not found! Check the title and try again.")
    else:
        st.warning("Please enter a movie or show name.")

# Commented out camera code for future use
# img_file = st.camera_input("Take a picture of a movie scene")
# if img_file is not None:
#     st.image(img_file, caption="Captured Image")