import streamlit as st
from css.media_selection_css import movie_section_css

def renderSelectionPage(page):
    #Page Title
    st.title("Select One to Get Recommendations")

    #Inital Movie And Tv Show Selection
    #Includes 20 Movies And Tv Shows for the user to select
    movie_selection = [
        {"Image": "mediaImages/StrangerThings.png","Title": "Stranger Things"},
        {"Image": "mediaImages/TheOffice.png","Title": "The Office (U.S.)"},
        {"Image": "mediaImages/Shameless.png","Title": "Shameless (U.S.)"},
        {"Image": "mediaImages/SquidGame.png","Title": "Squid Game"},
        {"Image": "mediaImages/CobraKai.png","Title": "Cobra Kai"},
        {"Image": "mediaImages/BreakingBad.png","Title": "Breaking Bad"},
        {"Image": "mediaImages/Narcos.png","Title": "Narcos"},
        {"Image": "mediaImages/TheWitcher.png","Title": "The Witcher"},
        {"Image": "mediaImages/PeakyBlinders.png","Title": "Peaky Blinders"},
        {"Image": "mediaImages/TheCrown.png","Title": "The Crown"},
        {"Image": "mediaImages/BirdBox.png","Title": "Bird Box"},
        {"Image": "mediaImages/TheIrishman.png","Title": "The Irishman"},
        {"Image": "mediaImages/MarriageStory.png","Title": "Marriage Story"},
        {"Image": "mediaImages/EnolaHolmes.png","Title": "Enola Holmes"},
        {"Image": "mediaImages/Extraction.png","Title": "Extraction"},
        {"Image": "mediaImages/TheSocialDilemma.png","Title": "The Social Dilemma"},
        {"Image": "mediaImages/MurderMystery.png","Title": "Murder Mystery"},
        {"Image": "mediaImages/TheTrialoftheChicago7.png","Title": "The Trial of the Chicago 7"},
        {"Image": "mediaImages/DolemiteIsMyName.png","Title": "Dolemite Is My Name"},
        {"Image": "mediaImages/Roma.png","Title": "ROMA"}
    ]

    #Applying css For Movie Selection Screen
    if page == "Selection Page":
        movie_section_css()

    #Creating columns and rows for movie selection screen
    num_cols = 4
    for i in range(0, len(movie_selection), num_cols):
        row = st.columns(num_cols)
        chunk = movie_selection[i : i + num_cols]

        #Creating Columns
        for col_idx, media in enumerate(chunk):
            #Creating Rows From Columns
            with row[col_idx]:
                with st.container(border=False, width="content"):
                    st.image(media["Image"])
                    if st.button(media["Title"]):
                        #Saving the selected Media
                        st.session_state.selected_movie = media["Title"]
                        #saving the media image
                        st.session_state.selected_movie_image = media["Image"]

                        st.session_state.page = "About Media"
                        st.rerun()
