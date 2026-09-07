import os

# Absolute path to this project's root (folder containing this config.py)
_BASE_DIR = os.path.abspath(os.path.dirname(__file__))
_SQLITE_PATH = os.path.join(_BASE_DIR, "watchlist.db")
_SQLITE_URI = "sqlite:///" + _SQLITE_PATH.replace("\\", "/")


class Config:
    '''
    General configuration parent class
    '''
    MOVIE_API_BASE_URL = "https://api.themoviedb.org/3/movie/{}?api_key={}"
    # No API key by default -> the app runs in OFFLINE DEMO MODE using the
    # bundled dataset (app/data/movies.csv). Set MOVIE_API_KEY for live data.
    MOVIE_API_KEY = os.environ.get("MOVIE_API_KEY")
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Zero-config SQLite by default. Override with the DATABASE_URL env var to
    # use Postgres/MySQL/etc. (preserves the original engine when set).
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", _SQLITE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_PHOTOS_DEST = "app/static/photos"

    # email configurations
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # simplemde configurations
    SIMPLEMDE_JS_IIFE = True
    SIMPLEMDE_USE_CDN = True


class ProdConfig(Config):
    '''
    Production configuration child class
    '''
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", Config.SQLALCHEMY_DATABASE_URI)


class TestConfig(Config):
    """
    Test configuration child class
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "sqlite:///" + os.path.join(_BASE_DIR, "watchlist_test.db").replace("\\", "/"),
    )


class DevConfig(Config):
    '''
    Development configuration child class
    '''
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", Config.SQLALCHEMY_DATABASE_URI)
    DEBUG = True


config_options = {
    "development": DevConfig,
    "production": ProdConfig,
    "test": TestConfig
}
