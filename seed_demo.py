"""
Idempotent demo seed for the Movie Browser & Recommender.

Creates the SQLite tables and a couple of demo accounts plus a few sample
reviews so the app shows populated content on first launch. Safe to run
repeatedly: it skips seeding when data already exists unless --force is given.

NOTE on the watchlist: in this app the watchlist is stored in the Flask
*session* (per-browser), not in the database, so it cannot be pre-seeded
server-side. The seed instead pre-populates demo users and reviews. The
movie catalogue itself ships as a bundled dataset (data/movies.json) and is
always available offline.

Usage:
    python seed_demo.py            # seed if empty
    python seed_demo.py --force    # wipe demo users/reviews and reseed
"""
import sys

from app import create_app, db
from app.models import User, Role, Review

DEMO_USERS = [
    {"username": "admin", "email": "admin@example.com", "password": "admin123",
     "role": "Administrator", "bio": "Demo administrator account."},
    {"username": "demo", "email": "demo@example.com", "password": "demo12345",
     "role": "User", "bio": "Demo viewer account."},
]

DEMO_REVIEWS = [
    {"username": "demo", "movie_id": 1, "movie_title": "The Shawshank Redemption",
     "review_title": "An all-time classic",
     "movie_review": "Hope is a good thing. A masterpiece of patient storytelling."},
    {"username": "admin", "movie_id": 3, "movie_title": "The Dark Knight",
     "review_title": "Best comic-book film ever",
     "movie_review": "Heath Ledger's Joker steals every scene. Tense from start to finish."},
]


def _get_or_create_role(name):
    role = Role.query.filter_by(name=name).first()
    if role is None:
        role = Role(name=name)
        db.session.add(role)
        db.session.flush()
    return role


def seed(force=False):
    app = create_app("development")
    with app.app_context():
        db.create_all()

        existing = User.query.count()
        if existing and not force:
            print(f"[seed] Database already has {existing} user(s); skipping. "
                  f"Use --force to reseed.")
            return

        if force:
            # Remove only the demo accounts (and their reviews) to stay idempotent.
            for u in DEMO_USERS:
                user = User.query.filter_by(username=u["username"]).first()
                if user:
                    Review.query.filter_by(user_id=user.id).delete()
                    db.session.delete(user)
            db.session.commit()
            print("[seed] --force: cleared existing demo users/reviews.")

        # Users
        for u in DEMO_USERS:
            if User.query.filter_by(username=u["username"]).first():
                continue
            role = _get_or_create_role(u["role"])
            user = User(username=u["username"], email=u["email"],
                        bio=u["bio"], role=role)
            user.password = u["password"]
            db.session.add(user)
        db.session.commit()

        # Reviews
        for r in DEMO_REVIEWS:
            author = User.query.filter_by(username=r["username"]).first()
            if author is None:
                continue
            dup = Review.query.filter_by(
                user_id=author.id, movie_id=r["movie_id"],
                review_title=r["review_title"]).first()
            if dup:
                continue
            review = Review(movie_id=r["movie_id"],
                            movie_title=r["movie_title"],
                            image_path="",
                            review_title=r["review_title"],
                            movie_review=r["movie_review"],
                            user=author)
            db.session.add(review)
        db.session.commit()

        print(f"[seed] Done. Users={User.query.count()} "
              f"Reviews={Review.query.count()}")
        print("[seed] Demo logins (sign in with EMAIL):")
        print("         admin@example.com / admin123")
        print("         demo@example.com  / demo12345")


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
