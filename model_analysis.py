import streamlit as st
import pandas as pd
from css.model_analysis_css import model_analysis_css
from media_recommendations import recommendationModel



#Showing Some details of the selected movie to the user!
def renderModelAnalysisPage(responses, page):
    #Loading CSS for Page
    if page == "Model Analysis":
        model_analysis_css()

    #Page Title
    st.title("The Recommendation Model's Relevance")
    #using pandas for data frame on response dictionary
    response_data = pd.DataFrame(st.session_state.responses)
    response_count = response_data["Response"].value_counts()
    st.bar_chart(response_count)

    #Variables for accuracy
    value_of_responses = 0
    accuracy = 0

    #Adding Up the response values
    for i in range(len(responses)):
        value_of_responses += responses[i]["Value"]

    #Calcautation accuracy
    accuracy = (value_of_responses / 10) * 100

    #Displaying Model accuracy
    st.markdown(f'<div class="accuracy">The Recommendation Model was <span>{accuracy:.1f}%</span> relevant!</div>', unsafe_allow_html=True)
    #Storing response details in string for display
    response_html = ""
    for i in range(len(responses)):
        response_html += f"""
            <div class = "response">
                <div class="media-title">Media Title: {responses[i]["Title"]}</div>
                <div class="media-genre">Your Response: {responses[i]["Response"]}</div>
            </div>
        """
    #Putting responses in container for html layout as these are unresponsive elements
    st.markdown(f"""
            <div class="response-container">
                {response_html}
            </div> """, unsafe_allow_html=True)

    if st.button("Get Descriptive Analysis"):
        st.session_state.page = "Descriptive Analysis"
        st.rerun()