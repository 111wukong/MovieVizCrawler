"""
RESTful API 路由 (Blueprints)

提供 JSON 格式的数据接口，支持跨域访问。
"""

import logging

from flask import Blueprint, jsonify, request

from movie_viz.models import Movie, db
from movie_viz.services.analyzer import MovieAnalyzer

logger = logging.getLogger(__name__)
api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/movies")
def api_movie_list():
    """
    电影列表 API

    GET /api/movies?keyword=&min_score=&page=
    """
    keyword = request.args.get("keyword", "").strip()
    min_score = request.args.get("min_score", 0, type=float)
    max_score = request.args.get("max_score", 10, type=float)
    genre = request.args.get("genre", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    per_page = min(per_page, 100)  # 限制单次最大条数

    movies, total, total_pages = MovieAnalyzer.search(
        keyword=keyword,
        min_score=min_score,
        max_score=max_score,
        genre=genre,
        page=page,
        per_page=per_page,
    )

    return jsonify({
        "code": 0,
        "data": {
            "movies": [m.to_dict() for m in movies],
            "total": total,
            "page": page,
            "total_pages": total_pages,
            "per_page": per_page,
        },
        "message": "success",
    })


@api_bp.route("/movies/<int:movie_id>")
def api_movie_detail(movie_id: int):
    """电影详情 API"""
    movie = db.session.get(Movie, movie_id)
    if not movie:
        return jsonify({"code": 404, "data": None, "message": "电影不存在"}), 404
    return jsonify({"code": 0, "data": movie.to_dict(), "message": "success"})


@api_bp.route("/stats/score")
def api_score_stats():
    """评分分布统计 API"""
    data = MovieAnalyzer.score_distribution()
    return jsonify({"code": 0, "data": data, "message": "success"})


@api_bp.route("/stats/year")
def api_year_stats():
    """年份分布统计 API"""
    data = MovieAnalyzer.year_distribution()
    return jsonify({"code": 0, "data": data, "message": "success"})


@api_bp.route("/stats/genre")
def api_genre_stats():
    """类型分布统计 API"""
    data = MovieAnalyzer.genre_distribution()
    return jsonify({"code": 0, "data": data, "message": "success"})


@api_bp.route("/stats/top-rated")
def api_top_rated():
    """评分最高电影 API"""
    limit = request.args.get("limit", 10, type=int)
    movies = MovieAnalyzer.top_rated(limit)
    return jsonify({
        "code": 0,
        "data": [m.to_dict() for m in movies],
        "message": "success",
    })


@api_bp.route("/stats/most-rated")
def api_most_rated():
    """最热门电影 API"""
    limit = request.args.get("limit", 10, type=int)
    movies = MovieAnalyzer.most_rated(limit)
    return jsonify({
        "code": 0,
        "data": [m.to_dict() for m in movies],
        "message": "success",
    })


@api_bp.route("/overview")
def api_overview():
    """数据概览 API"""
    total = Movie.query.count()
    avg_score = db.session.query(db.func.avg(Movie.score)).scalar()
    score_data = MovieAnalyzer.score_distribution()
    genre_data = MovieAnalyzer.genre_distribution()

    return jsonify({
        "code": 0,
        "data": {
            "total_movies": total,
            "average_score": round(float(avg_score), 2) if avg_score else 0,
            "score_distribution": score_data,
            "genre_distribution": genre_data,
        },
        "message": "success",
    })
