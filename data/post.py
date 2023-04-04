import datetime

import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    completed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    rating = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    done = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    user = orm.relationship('User')

    tags = orm.relationship('Tag', secondary='posts_with_tags', back_populates='posts')

    thread_messages = orm.relationship("ThreadMessage", back_populates='post')
