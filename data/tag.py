import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Tag(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tags'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)

    posts = orm.relationship("Post", secondary='posts_with_tags', back_populates='tags')
