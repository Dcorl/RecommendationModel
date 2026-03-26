import streamlit as st


def model_analysis_css():
    st.markdown(
        """
        <style>
        /*Main container*/
        .st-emotion-cache-1w723zb {
            max-width: 1000px;
        }
        /*Page Heading*/
        .st-emotion-cache-nl76d5 h1 {
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