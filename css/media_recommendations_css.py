import streamlit as st

def media_recommendations_css():
    st.markdown("""
        <style>
        /*Main Container*/
        [data-testid="stMainBlockContainer"] {
            max-width: 900px !important;
        }

        /*Page Heading*/
        [data-testid="stMainBlockContainer"] h1 {
            padding-bottom: 50px;
        }

        /*Media Details*/
        .media-title {
            font-size: 30px;
            padding-bottom: 8px;
        }
        .media-genre{
            font-size: 20px;
            padding-bottom: 20px;
        }
        .media-description {
            font-size: 18px;
            padding-bottom: 50px;
        }

        /*Button Width*/
        [data-testid="stBaseButton-secondary"] {
            width: 200px !important;
        }
        </style>
        """,
                unsafe_allow_html=True
                )