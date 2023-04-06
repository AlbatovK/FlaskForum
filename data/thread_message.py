import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class ThreadMessage(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'thread_messages'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    user = orm.relationship('User')

    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("posts.id"))

    post = orm.relationship('Post')
