import datetime

from flask import jsonify
from flask_apispec import MethodResource, doc, marshal_with
from flask_restful import Resource
from marshmallow import Schema, fields

from data import db_session
from data.post import Post


class PostResponseSchema(Schema):
    title = fields.String(default='title')
    content = fields.String(default='content')
    created_date = fields.DateTime(default=datetime.datetime.now())
    id = fields.Integer()
    user_ud = fields.Integer()
    completed = fields.Boolean()
    rating = fields.Integer()
    done = fields.Boolean()


class PostListResource(MethodResource, Resource):

    @doc(description='Получить все посты')
    @marshal_with(PostResponseSchema, code='200')
    def get(self):
        session = db_session.create_session()
        posts = session.query(Post).all()
        return jsonify(
            [
                x.to_dict(
                    only=('title', 'content', 'created_date',
                          'completed', 'user_id', 'id', 'rating', 'done')
                ) for x in posts]
        )
