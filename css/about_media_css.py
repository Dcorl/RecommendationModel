import streamlit as st
def about_media_css():
    st.markdown(
        """
        <style>
        /*Page Heading*/
        .st-emotion-cache-nl76d5 h1 {
            text-align: center;
            padding-bottom: 80px;
        }

        /*Media Details Container*/
        .st-emotion-cache-1w723zb {
            max-width: 1000px;
        }

        /*Media image*/
        .st-emotion-cache-7czcpc > img  {
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