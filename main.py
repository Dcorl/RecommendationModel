import streamlit as st
from media_selection import renderSelectionPage

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

if "selected_movie_image" not in st.session_state:
    st.session_state.selected_movie_image = None

if st.session_state.selected_movie is None:
    st.session_state.page = "Selection Page"
    renderSelectionPage(st.session_state.page)