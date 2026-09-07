from flask import (render_template, request, redirect,
                   url_for, abort, session, jsonify)
from . import main
from .forms import ReviewForm, UpdateProfile
from ..models import Review, User
from flask_login import login_required, current_user
from .. import db, photos
from ..recommender import get_all_movies, get_movie, get_recommendations, get_genres
import markdown2


# ── Movie browsing & recommendations ──────────────────────────────────────────

@main.route('/')
def index():
    genre = request.args.get('genre', '')
    search = request.args.get('search', '')
    movies = get_all_movies(genre=genre or None, search=search or None)
    genres = get_genres()
    watchlist_ids = session.get('watchlist', [])
    return render_template('index.html',
                           movies=movies,
                           genres=genres,
                           selected_genre=genre,
                           search=search,
                           watchlist_ids=watchlist_ids)


@main.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = get_movie(movie_id)
    if not movie:
        abort(404)
    recommendations = get_recommendations(movie_id)
    watchlist_ids = session.get('watchlist', [])
    reviews = Review.query.filter_by(movie_id=movie_id).all()
    return render_template('movie_detail.html',
                           movie=movie,
                           recommendations=recommendations,
                           watchlist_ids=watchlist_ids,
                           reviews=reviews)



# ── Watchlist ─────────────────────────────────────────────────────────────────

@main.route('/watchlist/toggle/<int:movie_id>', methods=['POST'])
def toggle_watchlist(movie_id):
    watchlist = session.get('watchlist', [])
    if movie_id in watchlist:
        watchlist.remove(movie_id)
        added = False
    else:
        watchlist.append(movie_id)
        added = True
    session['watchlist'] = watchlist
    return jsonify({'added': added, 'count': len(watchlist)})


@main.route('/watchlist')
def watchlist():
    watchlist_ids = session.get('watchlist', [])
    movies = [get_movie(mid) for mid in watchlist_ids]
    movies = [m for m in movies if m]
    return render_template('watchlist.html', movies=movies)


# ── Reviews ───────────────────────────────────────────────────────────────────

@main.route('/movie/review/new/<int:id>', methods=['GET', 'POST'])
@login_required
def new_review(id):
    form = ReviewForm()
    movie = get_movie(id)
    if movie is None:
        abort(404)

    if form.validate_on_submit():
        title = form.title.data
        review = form.review.data
        new_rev = Review(movie_id=id,
                         movie_title=movie['title'],
                         image_path='',
                         review_title=title,
                         movie_review=review,
                         user=current_user)
        new_rev.save_review()
        return redirect(url_for('main.movie_detail', movie_id=id))

    return render_template('new_review.html',
                           title=f"{movie['title']} review",
                           review_form=form,
                           movie=movie)


@main.route('/review/<int:id>')
def single_review(id):
    review = Review.query.get(id)
    if review is None:
        abort(404)
    format_review_title = markdown2.markdown(
        review.review_title, extras=["code-friendly", "fenced-code-blocks"])
    format_review = markdown2.markdown(
        review.movie_review, extras=["code-friendly", "fenced-code-blocks"])
    return render_template('review.html',
                           review=review,
                           format_review_title=format_review_title,
                           format_review=format_review)


# ── User profiles ─────────────────────────────────────────────────────────────

@main.route('/user/<uname>')
def profile(uname):
    user = User.query.filter_by(username=uname).first()
    if user is None:
        abort(404)
    return render_template('profile/profile.html', user=user, title=user.username)


@main.route('/user/<uname>/update', methods=['GET', 'POST'])
@login_required
def update_profile(uname):
    user = User.query.filter_by(username=uname).first()
    if user is None:
        abort(404)
    form = UpdateProfile()
    if form.validate_on_submit():
        user.bio = form.bio.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.profile', uname=user.username))
    return render_template('profile/update.html', form=form)


@main.route('/user/<uname>/update/pic', methods=['POST'])
@login_required
def update_pic(uname):
    user = User.query.filter_by(username=uname).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        user.profile_pic_path = f'photos/{filename}'
        db.session.commit()
    return redirect(url_for('main.profile', uname=uname))
