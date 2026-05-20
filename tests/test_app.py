"""
基础测试
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_imports():
    """测试模块导入"""
    from movie_viz import create_app
    app = create_app("testing")
    assert app is not None
    assert app.testing is True


def test_index_route():
    """测试首页"""
    from movie_viz import create_app
    app = create_app("testing")
    with app.test_client() as client:
        resp = client.get("/")
        assert resp.status_code == 200


def test_api_movies():
    """测试 API"""
    from movie_viz import create_app
    app = create_app("testing")
    with app.test_client() as client:
        resp = client.get("/api/movies")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["code"] == 0


def test_models():
    """测试模型"""
    from movie_viz.models import Movie
    assert hasattr(Movie, "to_dict")
    assert hasattr(Movie, "year")
    assert hasattr(Movie, "genres")
