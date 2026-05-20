"""
数据库连接与初始化
"""

import os
import logging
import shutil

from flask import Flask

from config import get_config
from .models import db, Movie

logger = logging.getLogger(__name__)


def init_db(app: Flask) -> None:
    """初始化数据库连接，兼容旧版 movie.db"""
    config = get_config()

    # 确保数据目录存在
    os.makedirs(config.DATA_DIR, exist_ok=True)

    old_db = os.path.join(config.BASE_DIR, "movie.db")
    new_db = os.path.join(config.DATA_DIR, "movie.db")

    # 根目录有旧数据库但 data/ 下没有 → 复制
    if os.path.exists(old_db) and not os.path.exists(new_db):
        logger.info("迁移旧版数据库: %s -> %s", old_db, new_db)
        shutil.copy2(old_db, new_db)

    db.init_app(app)

    with app.app_context():
        # 检查数据是否已存在
        inspector = db.inspect(db.engine)
        has_table = inspector.has_table(Movie.__tablename__)

        if has_table:
            count = Movie.query.count()
            logger.info("数据库就绪，当前记录数: %d", count)
        else:
            db.create_all()
            logger.info("数据库表已创建")

            # 如果旧数据库存在但还没导入数据，尝试导入
            if os.path.exists(new_db):
                count = Movie.query.count()
                logger.info("数据记录数: %d", count)
