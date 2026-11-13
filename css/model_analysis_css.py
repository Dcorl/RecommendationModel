import streamlit as st


def model_analysis_css():
    st.markdown(
        """
        <style>
        /*Main container*/
        [data-testid="stMainBlockContainer"] {
            max-width: 1000px;
        }
        /*Page Heading*/
        [data-testid="stMainBlockContainer"] h1 {
                text-align: center;
                padding-bottom: 50px;
        }
        .accuracy {
            padding-bottom: 40px;
            font-size: 28px;
            text-align: center;
        }

        .accuracy span {
            color: #83c9ff;
        }
        .response-container{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
        }
        .response{
            width: 23%;
            min-width: 200px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )