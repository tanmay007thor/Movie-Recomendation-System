import pickle
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

def fetch_poster(movie_id):
    """
    Fetch the poster for the movie using TMDb API.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url)
    data = data.json()
    poster_path = data.get('poster_path')
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return None

def recommend(movie, movies, similarity):
    """
    Recommend movies based on the selected movie.
    """
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], []  # Return empty lists if movie not found

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:  # Skip the first one because it's the same movie
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_movie = request.form["movie_name"].strip()
        
        # Load the movie list and similarity matrix from pickle files
        movies = pickle.load(open('model/movie_list.pkl', 'rb'))
        similarity = pickle.load(open('model/similarity.pkl', 'rb'))
        
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies, similarity)

        return render_template("index.html", movie_name=selected_movie, 
                               recommended_movie_names=recommended_movie_names,
                               recommended_movie_posters=recommended_movie_posters)
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
