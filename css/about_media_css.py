import streamlit as st
def about_media_css():
    st.markdown(
        """
        <style>
        /*Page Heading*/
        [data-testid="stMainBlockContainer"] h1 {
            text-align: center;
            padding-bottom: 80px;
        }

        /*Media Details Container*/
        [data-testid="stMainBlockContainer"] {
            max-width: 1000px;
        }

        /*Media image*/
        [data-testid="stImageContainer"] > img  {
            max-width: 90% !important;
        }

        /*Media details*/
        .media-title {
            font-size: 40px;
            padding-bottom: 20px;
        }

        .media-genre {
            font-size: 22px;
            padding-bottom: 20px;
        }

        .media-description {
            font-size: 18px;
            padding-bottom: 20px;
        }
        button:not(:disabled), [role="button"]:not(:disabled) {
            border-color: #a40120;
            color: #ffffff;
            }
        </style>
        """,
        unsafe_allow_html=True
    )