import streamlit as st
def movie_section_css():
    st.markdown(
        """
        <style>   
        /*Page Heading*/
        .st-emotion-cache-nl76d5 h1 {
            text-align: center;
        }

        /* Sets the maximum width of the main application container */
        .st-emotion-cache-1w723zb {
            max-width: 1200px;
        }

        /* Aligns & centers text in movie containers */
        .st-emotion-cache-1xhhvks p{
            text-align: center;
            font-size: larger;
        }

        /* Creates gap for spacing of rows for movie container */
        .st-emotion-cache-tn0cau {
            gap: 2rem
        }
        /*Cell Container*/
        .st-emotion-cache-1n6tfoc {
            width: 90%;
            align-items: center;
        }
        /*Movie cell background & border*/
        .st-emotion-cache-1gz5zxc {
            background: black;
            border: 1px solid rgb(0 0 0 / 20%)
        }
        /*Mvoie Cell Images*/
        .st-emotion-cache-7czcpc {
            border-radius: 0.8rem;
        }
        /*Movie cell button*/
        .st-emotion-cache-1anq8dj{
            width: 250px;
            background: #780000;

        }
        </style>
        """,
        unsafe_allow_html=True
    )