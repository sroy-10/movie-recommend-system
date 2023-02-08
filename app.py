import ast
import pickle

import requests
import streamlit as st


def fetch_movie_details(movie_id):
    data = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=3dfb37553e53bedd6e83d2198ce70d2b').json()
    return data


def fetch_movie_poster(movie_id='', json_data=''):
    if len(json_data) == 0:
        if movie_id == '':
            return ''
        data = fetch_movie_details(movie_id)
    else:
        data = json_data
    return 'https://image.tmdb.org/t/p/w500'+data['poster_path']


def recommend_movie(data, data_similarity, movie_name, top=5):
    # fetching the movie index
    idx = data[data['title'] == movie_name].index[0]

    # selecting the top similarity scores for movies
    similarity_score = list(enumerate(data_similarity[idx]))
    similarity_score = sorted(
        similarity_score, reverse=True, key=lambda x: x[1])[1:top+1]

    # recommend movies
    recommend_moviename = []
    recommend_movieidx = []
    recommend_movieposter = []
    recommend_moviedetails = []

    for i in similarity_score:
        recommend_movieidx.append(i)
        recommend_moviename.append(data.iloc[i[0]]['title'])

        # movie posters and details
        movie_json_data = fetch_movie_details(movie_id=data.iloc[i[0]]['id'])
        recommend_moviedetails.append(movie_json_data)
        recommend_movieposter.append(
            fetch_movie_poster(json_data=movie_json_data))

    return recommend_moviename, recommend_movieidx, recommend_movieposter, recommend_moviedetails


st.title("Movie Recommender System")

movies = pickle.load(open('movies.pkl', 'rb'))
movies_similarity_score = pickle.load(
    open('movies_similarity_score.pkl', 'rb'))
movies_list = movies['title'].values

selected_movie_name = st.selectbox(
    'Search Movies',
    (movies_list)
)

# slider to choose the number of recommended movies
top = st.slider(label="How many recommended movies?",
                min_value=1, max_value=10, value=5, step=1)

# recommend button
if st.button('Recommend'):
    recommend_moviename, recommend_movieidx, recommend_movieposter, recommend_moviedetails = recommend_movie(
        movies, movies_similarity_score, selected_movie_name, top=top)

    for idx, val in enumerate(recommend_movieidx):
        col = st.columns(2)
        with st.container():
            st.subheader(movies.iloc[val[0]]['title'])
            col = st.columns(2)
            with col[0]:
                st.image(recommend_movieposter[idx])
            with col[1]:
                st.markdown(recommend_moviedetails[idx]['overview'])
                st.subheader(
                    f"{round(recommend_moviedetails[idx]['vote_average'],2)} :star:")
                st.text(
                    f"Vote Count: {recommend_moviedetails[idx]['vote_count']}")
                st.text(
                    f"Popularity: {recommend_moviedetails[idx]['popularity']}")

                imdb_link = "https://www.imdb.com/title/" + \
                    recommend_moviedetails[idx]['imdb_id']
                original_link = recommend_moviedetails[idx]['homepage']
                link = f'<small>[IMDB]({imdb_link})&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;||&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Official Website]({original_link})</small>'
                st.markdown(link, unsafe_allow_html=True)
