import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sb
import squarify
from css.descriptive_analysis_css import  descriptive_analysis_css
#Descriptive Analysis

#1.Distribution of top 10 Genres represented by treemap
def renderDescriptiveAnalysisPage(dataset, page):
    if page == "Descriptive Analysis":
        descriptive_analysis_css()

    #Creaning up genre column
    genres = dataset["Genre"].str.split(",")

    #Screading new rows for media with multiple genres and only contains the word no spaces
    genres = genres.explode().str.strip()

    #counting genres in dataset
    genre_count = genres.value_counts().head(10)

    #Setting up treemap data and labels
    tree_map_data = genre_count.values
    genres_labels = genre_count.index

    #Creating treemap figure
    tree_map, ax = plt.subplots(figsize=(30, 30))

    #Applying Color palette (using seaborn for colors) labels and data
    squarify.plot(sizes = tree_map_data, label= genres_labels, text_kwargs= {"fontsize":30}, color=sb.color_palette("Spectral", len(tree_map_data)), pad=1, ax=ax)

    #displaying treemap in streamlit(application)
    st.title("Descriptive Analysis")
    st.write("Distribution of top 10 Genres")
    st.pyplot(tree_map)

    #2.The most common genre in the dataset represented by pie chart
    #getting top 5 genres
    top_five_genres = genre_count.head(5)
    #Creating pi chart figure
    pie_chart, ax = plt.subplots(figsize=(10, 10))
    ax.pie(
        top_five_genres.values,
        labels= top_five_genres.index,
        autopct="%1.1f%%",
    )
    ax.set_title("Top 5 Most Common Genres")
    st.pyplot(pie_chart)
