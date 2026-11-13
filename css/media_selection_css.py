import streamlit as st
def movie_section_css():
    st.markdown(
        """
        <style>
        /* Selectors use Streamlit's data-testid attributes and the st-key-* classes
           added by keyed containers. Both are stable across Streamlit releases,
           unlike the generated .st-emotion-cache-* class names. */

        /*Page Heading*/
        [data-testid="stMainBlockContainer"] h1 {
            text-align: center;
        }

        /* Sets the maximum width of the main application container */
        [data-testid="stMainBlockContainer"] {
            max-width: 1200px;
        }

        /* Creates gap for spacing of rows for movie container */
        [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
            gap: 2rem;
        }

        /*Movie cell background & border*/
        [data-testid="stColumn"]:has([class*="st-key-media_card_"]) {
            background: black;
            border: 1px solid rgb(0 0 0 / 20%);
        }

        /*Cell Container: centred horizontally within its column*/
        [class*="st-key-media_card_"] {
            width: 90%;
            align-items: center;
            align-self: center;
        }

        /* Aligns & centers text in movie containers */
        [class*="st-key-media_card_"] p {
            text-align: center;
            font-size: larger;
        }

        /*Movie Cell Images*/
        [class*="st-key-media_card_"] [data-testid="stImageContainer"],
        [class*="st-key-media_card_"] [data-testid="stImageContainer"] img {
            border-radius: 0.8rem;
        }

        /*Movie cell button*/
        [class*="st-key-media_card_"] [data-testid="stBaseButton-secondary"] {
            width: 250px;
            max-width: 100%;
            background: #780000;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
