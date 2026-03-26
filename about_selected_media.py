import streamlit as st
from css.about_media_css import about_media_css



#Showing Some details of the selected movie to the user!
def renderAboutSelectedMediaPage(dataset, selected_media, media_image, page):

    #Loading CSS for Page
    if page == "About Media":
        about_media_css()

    #Page Title
    st.title("Details about the media you've selected")

    #Searching for movie details
    media_details = dataset.loc[dataset['Title'] == selected_media].iloc[0]
    #Creating columns
    image_col, detail_col = st.columns(2)

    #Displaying Movie Content From Found Media Search
    with image_col:
        st.image(media_image, width=800)

    with detail_col:
        st.markdown(f'<div class="media-title">{media_details["Title"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="media-genre">{media_details["Genre"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="media-description">{media_details["Description"]}</div>', unsafe_allow_html=True)
        if st.button("Get Recommendations!"):
            st.session_state.page = "Recommendations"
            st.rerun()