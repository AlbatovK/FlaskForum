import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class PostWithTags(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'posts_with_tags'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('posts.id'))

    tag_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('tags.id'))
