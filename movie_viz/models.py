"""
Movie model — maps to the legacy `movie250` table.

Note: the original schema has a column `instroduction` (typo preserved
for backward compatibility). A property alias exposes it as `.introduction`.
"""

from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Movie(db.Model):
    """豆瓣电影 TOP250 条目"""
    __tablename__ = "movie250"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    info_link = db.Column(db.Text)
    pic_link = db.Column(db.Text)
    cname = db.Column(db.String(200))
    ename = db.Column(db.String(200))
    score = db.Column(db.Float)
    rated = db.Column(db.Integer)
    # Legacy column name preserved from original schema
    instroduction = db.Column(db.Text)
    info = db.Column(db.Text)

    # ------------------------------------------------------------------
    # Friendly alias for the misspelled column
    # ------------------------------------------------------------------
    @property
    def introduction(self) -> str | None:
        return self.instroduction

    # ------------------------------------------------------------------
    # Computed properties (parsed from the `info` text blob)
    # ------------------------------------------------------------------
    @property
    def year(self) -> int | None:
        if not self.info:
            return None
        import re
        m = re.search(r"(\d{4})", self.info)
        return int(m.group(1)) if m else None

    @property
    def genres(self) -> list[str]:
        if not self.info:
            return []
        import re
        parts = re.split(r"\s{2,}", self.info.strip())
        return [g.strip() for g in parts[-1].split() if g.strip()] if len(parts) >= 3 else []

    @property
    def directors(self) -> list[str]:
        if not self.info:
            return []
        import re
        m = re.search(r"导演:\s*(.*?)(?:\s{2,}|$)", self.info)
        if m:
            return [d.strip() for d in re.split(r"[/、]", m.group(1)) if d.strip()]
        return []

    @property
    def casts(self) -> list[str]:
        if not self.info:
            return []
        import re
        m = re.search(r"主演:\s*(.*?)(?:\s{2,}|$)", self.info)
        if m:
            return [c.strip() for c in re.split(r"[/、]", m.group(1)) if c.strip()]
        return []

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "cname": self.cname,
            "ename": self.ename,
            "score": self.score,
            "rated": self.rated,
            "introduction": self.introduction,
            "info_link": self.info_link,
            "pic_link": self.pic_link,
            "year": self.year,
            "genres": self.genres,
            "directors": self.directors,
            "casts": self.casts[:5],
        }

    def __repr__(self) -> str:
        return f"<Movie {self.id}: {self.cname} ({self.score})>"
