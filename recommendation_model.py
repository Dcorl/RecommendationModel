# This is a machine leaning model that uses cosine similarly after transforming the data
# which is textual content into vectors to determine how similar other movie's / tv shows
# are based on what the user selected and the key features of the selection (Title, Description and Genre)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommendationModel(dataset, selectedTitle):
    #Key Features Of Dataset (Title, Description and Genre)
    dataset["KeyFeatures"] = (dataset["Title"] + ' ' + dataset["Description"] + ' ' + dataset["Genre"])
    #Ignoring Common English Words like and, is, or... and vectorizing remaining textual content from key features.
    vectorizer = TfidfVectorizer(stop_words='english')
    vectorized_features = vectorizer.fit_transform(dataset["KeyFeatures"])
    #Determining similarity with cosine similarity function
    similarity_matrix = cosine_similarity(vectorized_features)

    #Getting selected media index via title
    selected_media_index = dataset[dataset["Title"] == selectedTitle].index.values[0]


    similarity_score = list(enumerate(similarity_matrix[selected_media_index]))
    sorted_media_by_similarity_score = sorted(similarity_score, key=lambda x: x[1], reverse=True)

    top_media = []

    for i in sorted_media_by_similarity_score[1:11]:
        similar_media_index = i[0]
        title_of_similar_media = dataset.iloc[similar_media_index]["Title"]
        top_media.append(title_of_similar_media)

    return top_media