from flask import Flask, render_template, request, jsonify
from recommender import MovieRecommender
import os

app = Flask(__name__)

# Initialize Recommender
# Use absolute path to be safe
DATA_DIR = "/Users/ryanoliver/Projects/movie_reccomendation/ml-32m"
recommender = MovieRecommender(DATA_DIR)

# Load data on startup (this might take a moment)
print("Initializing Recommender System...")
recommender.load_data()
recommender.train_model()
print("Recommender System Ready!")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def get_recommendation():
    data = request.json
    movie_name = data.get('movie_name')
    
    if not movie_name:
        return jsonify({"error": "Movie name is required"}), 400
    
    recommendations = recommender.recommend(movie_name)
    
    if recommendations is None:
        return jsonify({"error": "Movie not found"}), 404
        
    return jsonify(recommendations)

@app.route('/search', methods=['GET'])
def search_movies():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = recommender.search_titles(query)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
