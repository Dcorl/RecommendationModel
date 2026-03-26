import streamlit as st

def media_recommendations_css():
    st.markdown("""
        <style>
        /*Main Container*/
        .st-emotion-cache-1w723zb {
            max-width: 900px !important;
        }

        /*Page Heading*/
        .st-emotion-cache-nl76d5 h1 {
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
        .st-emotion-cache-1anq8dj {
            width: 200px !important;
        }
        </style>
        """,
                unsafe_allow_html=True
                )