import pickle
import requests
import difflib
from flask import Flask, request, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



app = Flask(__name__)

movies_data = pickle.load(open("movies_data.pkl", "rb"))
top_50_movie = pickle.load(open("top_50_movie", "rb"))
movie_title = movies_data["title"].values

selected_features = ['cast', 'director', 'tagline', 'genres', "keywords"]
for feature in selected_features:
    movies_data[feature] = movies_data[feature].fillna('')
combined_features = movies_data['genres'] + ' ' + movies_data['keywords'] + ' ' + movies_data['tagline'] + ' ' + \
                    movies_data['cast'] + ' ' + movies_data['director']
vectorizer = TfidfVectorizer()
feature_vectors = vectorizer.fit_transform(combined_features)
cosine_sim = cosine_similarity(feature_vectors, feature_vectors)



api = "3dba6d71afff982834edbbc4d1c6d464"

def fetch_poster(movie_id):
        response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key=3dba6d71afff982834edbbc4d1c6d464" \
                                .format(movie_id))
        data = response.json()
        return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]


def MovieRecommender(movies_data, selected_movie_name, rec_count=5):
        index_of_the_movie = movies_data[movies_data.title == selected_movie_name]['index'].values[0]
        similarity_score = list(enumerate(cosine_sim[index_of_the_movie]))

        sorted_similar_movies = sorted(similarity_score, key=lambda x: x[1], reverse=True)

        i = 1
        Recommended_Movies = []
        MoviePosters = []
        MovieInfo = []
        for movie in sorted_similar_movies:
            index = movie[0]
            title_from_index = movies_data[movies_data.index == index]['title'].values[0]

            if i < rec_count + 2:
                Recommended_Movies.append(title_from_index)
                MoviePosters.append(fetch_poster(movies_data.iloc[index]["id"]))

                MovieInfo.append({"overview": movies_data.iloc[index]["overview"],
                                  "genres": movies_data.iloc[index]["genres"],
                                  "vote_average": movies_data.iloc[index]["vote_average"],
                                  "director": movies_data.iloc[index]["director"],
                                  "original_title": movies_data.iloc[index]["original_title"]})

                # "company": re.split(': |,|\+', movies_data.iloc[index]["production_companies"])[1]. \
                # strip("'").strip('"')

                i += 1

        return Recommended_Movies, MoviePosters, MovieInfo



@app.route("/Movie_Name", methods=["POST","GET"])
def Movie_Name():
    try:
        if request.method == "POST":
            written_movie_name = request.form["input_id"]
            list_of_all_titles = movies_data['title'].tolist()
            find_close_match = difflib.get_close_matches(written_movie_name, list_of_all_titles)
            try:
                actual_movie_name = close_match = find_close_match[0]


            except:
                actual_movie_name="Inglourious Basterds" 

            
            rec_count = 7
            recommendations, MoviePosters, MovieInfo = MovieRecommender(movies_data, actual_movie_name,
                                                                    rec_count=rec_count)
            for i in range(8):                
                MovieInfo[i]["MoviePoster"] = MoviePosters[i]  

            random_movies = top_50_movie.sample(18)
            images_paths = []
            for i in random_movies["id"]:
                images_paths.append(fetch_poster(i))

            titles = random_movies["title"].tolist()

            img_title = []
            for i in range(len(random_movies)):
                img_title.append([images_paths[i], titles[i]])

            selected_movie = MovieInfo[0]["original_title"]                                             
            
            return render_template("recsystem.html", MovieInfo=MovieInfo, img_title=img_title, selected_movie=selected_movie)
    


        else:
           return "An unexpected error has occurred! Movie not found! Try another movie name"
    except:
        return "An unexpected error has occurred! Movie not found! Try another movie name"   
        
   
@app.route('/process_image', methods=['POST'])
def process_image():

    random_movies = top_50_movie.sample(18)
    images_paths = []
    for i in random_movies["id"]:
        images_paths.append(fetch_poster(i))

    titles = random_movies["title"].tolist()

    img_title = []
    for i in range(len(random_movies)):
        img_title.append([images_paths[i], titles[i]])


    movie_name = request.form['image_id']
    # Do something with the image ID
    rec_count = 7
    recommendations, MoviePosters, MovieInfo = MovieRecommender(movies_data, movie_name,
                                                                    rec_count=rec_count)
    for i in range(8):                
        MovieInfo[i]["MoviePoster"] = MoviePosters[i]       

    selected_movie = MovieInfo[0]["original_title"]

    return render_template("recsystem.html", MovieInfo=MovieInfo, img_title=img_title, selected_movie=selected_movie)
 


@app.route('/')
def home():
    random_movies = top_50_movie.sample(18)
    images_paths = []
    for i in random_movies["id"]:
        images_paths.append(fetch_poster(i))

    titles = random_movies["title"].tolist()

    img_title = []
    for i in range(len(random_movies)):
        img_title.append([images_paths[i], titles[i]])


    movie_name = "Inglourious Basterds"
    rec_count = 7
    recommendations, MoviePosters, MovieInfo = MovieRecommender(movies_data, movie_name,
                                                                    rec_count=rec_count)
    for i in range(8):                
        MovieInfo[i]["MoviePoster"] = MoviePosters[i]  

    selected_movie = MovieInfo[0]["original_title"]                                             

    return render_template("recsystem.html", img_title=img_title, MovieInfo=MovieInfo, selected_movie=selected_movie)


if __name__ == '__main__':
    app.run(debug=True, port=int("3000"), host="0.0.0.0")