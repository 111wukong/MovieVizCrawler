"""
应用配置模块

支持多环境配置（development / production / testing），
通过环境变量 FLASK_ENV 或 APP_ENV 切换。
"""

import os
from datetime import timedelta


class BaseConfig:
    """基础配置"""
    PROJECT = "MovieVizCrawler"
    VERSION = "2.0.0"

    # 路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")

    # 数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Session
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # 爬虫
    CRAWL_INTERVAL_HOURS = 24
    CRAWL_USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Pagination
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(BaseConfig):
    """开发环境"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BaseConfig.DATA_DIR, 'movie.db')}",
    )


class ProductionConfig(BaseConfig):
    """生产环境"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BaseConfig.DATA_DIR, 'movie.db')}",
    )


class TestingConfig(BaseConfig):
    """测试环境"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """获取当前环境配置"""
    env = os.environ.get("FLASK_ENV") or os.environ.get("APP_ENV") or "development"
    return config_map.get(env, config_map["default"])
