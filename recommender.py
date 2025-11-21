import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import os

class MovieRecommender:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.ratings_file = os.path.join(data_dir, "ratings.csv")
        self.movies_file = os.path.join(data_dir, "movies.csv")
        self.model = None
        self.movie_sparse_matrix = None
        self.movie_titles = None
        self.df_filtered = None

    def load_data(self):
        print("Loading data...")
        try:
            ratings = pd.read_csv(self.ratings_file)
            movies = pd.read_csv(self.movies_file)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            raise

        print(f"Data loaded. Ratings: {ratings.shape}, Movies: {movies.shape}")
        
        # Merge
        df = pd.merge(ratings, movies, on="movieId")
        df = df[['userId', 'title', 'rating']]
        
        # Filter Popular Movies
        movie_count = df['title'].value_counts()
        min_movie_ratings = 50
        popular_movies = movie_count[movie_count >= min_movie_ratings].index
        df_filtered = df[df['title'].isin(popular_movies)]
        
        # Filter Active Users
        user_count = df['userId'].value_counts()
        min_user_ratings = 50
        active_users = user_count[user_count >= min_user_ratings].index
        df_filtered = df_filtered[df_filtered['userId'].isin(active_users)]
        
        print(f"Filtered dataframe shape: {df_filtered.shape}")
        
        # Create Sparse Matrix
        # Convert to categorical for efficiency and mapping
        df_filtered['title'] = df_filtered['title'].astype('category')
        df_filtered['userId'] = df_filtered['userId'].astype('category')
        
        self.movie_sparse_matrix = csr_matrix(
            (df_filtered['rating'], 
             (df_filtered['title'].cat.codes, df_filtered['userId'].cat.codes))
        )
        
        self.movie_titles = df_filtered['title'].cat.categories
        self.df_filtered = df_filtered
        
        print("Sparse matrix created.")

    def train_model(self):
        print("Training KNN model...")
        self.model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
        self.model.fit(self.movie_sparse_matrix)
        print("Model trained.")

    def recommend(self, movie_name, k=5):
        if self.model is None:
            raise Exception("Model not trained. Call load_data() and train_model() first.")
            
        if movie_name not in self.movie_titles:
            return None # Movie not found
        
        movie_index = self.movie_titles.get_loc(movie_name)
        
        distances, indices = self.model.kneighbors(
            self.movie_sparse_matrix[movie_index, :].reshape(1, -1),
            n_neighbors=k+1
        )
        
        recommendations = []
        for i in range(1, len(distances.flatten())):
            idx = indices.flatten()[i]
            dist = distances.flatten()[i]
            recommendations.append({
                "title": self.movie_titles[idx],
                "similarity": 1 - dist # Convert distance to similarity score roughly
            })
            
        return recommendations

    def search_titles(self, query, limit=10):
        """Helper to search for movie titles for autocomplete"""
        if self.movie_titles is None:
            return []
        
        query = query.lower()
        results = [title for title in self.movie_titles if query in title.lower()]
        return results[:limit]
