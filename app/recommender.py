"""
Content-based movie recommender.

OFFLINE-FIRST: loads the bundled dataset shipped with the project so the
catalogue, search and recommendations all work on first launch with no API
key and no network. Prefers the canonical data/movies.json at the project
root; falls back to the legacy app/data/movies.csv if the JSON is missing.
"""
import os
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_df = None
_cosine_sim = None

_APP_DIR = os.path.dirname(__file__)
_ROOT_DIR = os.path.dirname(_APP_DIR)
_JSON_PATH = os.path.join(_ROOT_DIR, 'data', 'movies.json')
_CSV_PATH = os.path.join(_APP_DIR, 'data', 'movies.csv')


def _read_dataset():
    """Read the bundled movie dataset into a DataFrame (JSON preferred)."""
    if os.path.exists(_JSON_PATH):
        with open(_JSON_PATH, 'r', encoding='utf-8') as f:
            return pd.DataFrame(json.load(f))
    return pd.read_csv(_CSV_PATH)


def _load():
    global _df, _cosine_sim
    if _df is not None:
        return
    _df = _read_dataset()
    _df['combined'] = _df['genres'].fillna('') + ' ' + _df['overview'].fillna('')
    tfidf = TfidfVectorizer(stop_words='english')
    matrix = tfidf.fit_transform(_df['combined'])
    _cosine_sim = cosine_similarity(matrix, matrix)


def get_all_movies(genre=None, search=None):
    _load()
    df = _df.copy()
    if genre:
        df = df[df['genres'].str.contains(genre, case=False, na=False)]
    if search:
        df = df[df['title'].str.contains(search, case=False, na=False)]
    return df.to_dict('records')


def get_movie(movie_id):
    _load()
    row = _df[_df['id'] == int(movie_id)]
    return row.iloc[0].to_dict() if not row.empty else None


def get_recommendations(movie_id, n=6):
    _load()
    matches = _df[_df['id'] == int(movie_id)]
    if matches.empty:
        return []
    idx = matches.index[0]
    scores = list(enumerate(_cosine_sim[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:n + 1]
    return [_df.iloc[i].to_dict() for i, _ in scores]


def get_genres():
    _load()
    genres = set()
    for g in _df['genres'].dropna():
        for part in g.split():
            genres.add(part)
    return sorted(genres)
