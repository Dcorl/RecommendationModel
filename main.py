import streamlit as st
import pandas as pd
from media_selection import renderSelectionPage
from about_selected_media import renderAboutSelectedMediaPage
from media_recommendations import renderRecommendationsPage
from model_analysis import renderModelAnalysisPage
from descriptive_analysis import renderDescriptiveAnalysisPage

#Importing Dataset Containing Movies & TV Shows
media_dataset = pd.read_csv('dataset/movies_and_tv_shows_dataset.csv')

#Setting default page and selected media image states for routing
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

if "selected_movie_image" not in st.session_state:
    st.session_state.selected_movie_image = None

#Routing To Different Pages Based On Session States
if st.session_state.selected_movie is None:
    st.session_state.page = "Selection Page"
    renderSelectionPage(st.session_state.page)

elif st.session_state.page == "About Media":
    renderAboutSelectedMediaPage(
        media_dataset, st.session_state.selected_movie,
        st.session_state.selected_movie_image, st.session_state.page
    )
elif st.session_state.page == "Recommendations":
    renderRecommendationsPage(
        media_dataset, st.session_state.selected_movie, st.session_state.page
    )
elif st.session_state.page == "Model Analysis":
    renderModelAnalysisPage(
        st.session_state.responses, st.session_state.page
    )
elif st.session_state.page == "Descriptive Analysis":
        renderDescriptiveAnalysisPage(media_dataset, st.session_state.page)