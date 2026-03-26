import streamlit as st
from css.media_recommendations_css import media_recommendations_css
from recommendation_model import recommendationModel

#Showing Some details of the selected movie to the user!
def renderRecommendationsPage(dataset, selected_media,page):
    #getting machine learning output
    similar_media = recommendationModel(dataset, selected_media)

    #Loading CSS for Page
    if page == "Recommendations":
        media_recommendations_css()

    #track the state of each recommendation, starting from 0
    if "recommendation_number" not in st.session_state:
        st.session_state.recommendation_number = 0

    #Saving user responses for later
    if "responses" not in st.session_state:
        st.session_state.responses = []

    #If the recommendations are over, switch state to check results
    if st.session_state.recommendation_number >= len(similar_media):
        st.session_state.page = "Model Analysis"
        st.rerun()

    #Page Title
    st.title("Does This Recommendation Interest You?")

    #Displaying Movie Content From Found Media Search
    current_recommendation = similar_media[st.session_state.recommendation_number]
    recommendation_details = dataset.loc[dataset['Title'] == current_recommendation].iloc[0]
    st.markdown(f'<div class="media-title">{recommendation_details["Title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="media-genre">{recommendation_details["Genre"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="media-description">{recommendation_details["Description"]}</div>', unsafe_allow_html=True)

    #Displaying User Choices Within Columns
    #These Choices represent number values for scoring
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Yes"):
            st.session_state.responses.append({
                 "Title": current_recommendation,
                 "Response": "Yes",
                 "Value": 1
             })
            st.session_state.recommendation_number += 1
            st.rerun()
    with col2:
        if st.button("Maybe"):
            st.session_state.responses.append({
                "Title": current_recommendation,
                "Response": "Maybe",
                "Value": 0.5
             })
            st.session_state.recommendation_number += 1
            st.rerun()
    with col3:
        if st.button("No"):
            st.session_state.responses.append({
                "Title": current_recommendation,
                "Response": "No",
                "Value": 0
            })
            st.session_state.recommendation_number += 1
            st.rerun()


